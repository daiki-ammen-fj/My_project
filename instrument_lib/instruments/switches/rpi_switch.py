"""Driver for RPI GPIO control."""

import platform

if "rpi" not in platform.platform():
    pass  # RPI GPIO control works on RPIs only, don't define class on other platforms
else:
    from gpiozero import DigitalOutputDevice  # type: ignore
    from gpiozero.pins.lgpio import LGPIOFactory  # type: ignore

    from instrument_lib.instruments.instrument import Instrument, InstrumentIdentificationInfo
    from instrument_lib.utils.gpio_pin import GPIOPin

    __all__ = ["RPISwitch"]

    class RPISwitch(Instrument):
        """RPI Switch class."""

        def __init__(self) -> None:
            """Constructor."""
            self._factory: LGPIOFactory = LGPIOFactory()
            self._devices: dict[GPIOPin, DigitalOutputDevice] = {}
            self._is_connected: bool = False
            self.identification: InstrumentIdentificationInfo

        def connect(self) -> None:
            """Connect to specified pins."""
            self._is_connected = True

        def close(self) -> None:
            """Disconnect from specified pins."""
            self._is_connected = False

            for device in self._devices.values():
                device.close()

            self._devices = {}

        def identify(self) -> InstrumentIdentificationInfo:
            """Instrument Identification."""
            host_info = platform.uname()
            self.identification = InstrumentIdentificationInfo(
                manufacturer="raspberry_pi_ltd",
                model="raspberry-pi-5",  # TODO: How to get model?,
                serial_number="",
                firmware=host_info.version,
            )
            return self.identification

        def set(self, pin: GPIOPin) -> None:
            """Set pin to logic high."""
            if self._devices.get(pin) is None:
                self._devices[pin] = DigitalOutputDevice(pin.pin, pin_factory=self._factory)

            try:
                self._devices[pin].on()
            except AttributeError as e:
                raise ValueError(f"Invalid pin {pin}, pin is not connected.") from e

        def clear(self, pin: GPIOPin) -> None:
            """Clear pin to logic low."""
            if self._devices.get(pin) is None:
                self._devices[pin] = DigitalOutputDevice(pin.pin, pin_factory=self._factory)

            try:
                self._devices[pin].off()
            except AttributeError as e:
                raise ValueError(f"Invalid pin {pin}, pin is not connected.") from e
