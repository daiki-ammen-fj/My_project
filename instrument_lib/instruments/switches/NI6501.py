"""Driver for NI 6501 USB Switch."""

import platform


if "Windows" in platform.platform() or (
    "Linux" in platform.platform() and "rpi" not in platform.platform()
):
    import nidaqmx as nd  # type: ignore

    from instrument_lib.instruments.instrument import SCPIInstrument
    from instrument_lib.utils.identification import InstrumentIdentificationInfo
    from instrument_lib.utils.gpio_pin import GPIOPin

    class NISwitch(SCPIInstrument):
        """NI Switcher.

        This instrument controls a set of switches.
        """

        def __init__(self) -> None:
            """Create the object."""
            self.device = self._get_device()
            self.connected = bool(self.device is not None)
            self.lines: dict[GPIOPin, str] = self._get_lines()

        def identify(self) -> InstrumentIdentificationInfo:
            """Instrument identification."""
            driver_version = self.system_.driver_version
            self.identification = InstrumentIdentificationInfo(
                manufacturer="National Instruments",
                model=self.device.product_type,
                serial_number=self.device.dev_serial_num,
                firmware=f"{driver_version.major_version}.{driver_version.minor_version}.{driver_version.update_version}",
            )
            return self.identification

        def _get_lines(self) -> dict[GPIOPin, str]:
            """Gets all ports and all lines in a dictionary."""
            if not self.connected:
                return {}
            actual_lines = list(self.device.do_lines)
            lines: dict[GPIOPin, str] = {}
            for line in actual_lines:
                line_name = line.name.split("/")
                port = int(line_name[1].strip("port"))
                line_ = int(line_name[2].strip("line"))
                pin = GPIOPin((port, line_))
                lines[pin] = line.name

            return lines

        def _get_device(self) -> nd.system.device.Device:
            """Get the nd device object."""
            self.system_ = nd.system.system.System()
            devices = list(self.system_.devices)
            for device in devices:
                if "USB-6501" == device.product_type:
                    return device

        def _is_device_connected(self) -> bool:
            """Checks for device existince."""
            return self.connected

        def connect(self) -> None:
            """Connect."""
            self.device = self._get_device()
            self.connected = True

        def close(self) -> None:
            """Safeuly close task."""
            if self.device is not None:
                self.device = None
                self.connected = False

        def set(self, pin: GPIOPin) -> None:
            """Sets the port/line combination to high."""
            try:
                channel_name = self.lines[pin]
            except AttributeError as e:
                raise ValueError("Invalid port or line supplied.") from e
            else:
                with nd.Task() as task:
                    task.do_channels.add_do_chan(channel_name)
                    task.write(True)

        def clear(self, pin: GPIOPin) -> None:
            """Sets the port/line combination to low."""
            try:
                channel_name = self.lines[pin]
            except AttributeError as e:
                raise ValueError("Invalid port or line supplied.") from e
            else:
                with nd.Task() as task:
                    task.do_channels.add_do_chan(channel_name)
                    task.write(False)

else:
    pass
