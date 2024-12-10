"""Instrument driver for KS_E36300_PS."""

from typing import Optional
from instrument_lib.utils import GPIBNumber
from instrument_lib.instruments.instrument import SCPIInstrument


class KS_E36300_PS(SCPIInstrument):  # noqa: N801
    """KS_E36300_PS class."""

    ACCEPTED_MODELS = [
        "E36312A",
        "E36231A",
    ]

    def __init__(
        self,
        gpib: GPIBNumber | None = None,
        ip_address: str | None = None,
        usb: tuple[str, str, str] | None = None,
        wireless: bool = False,
    ):
        """Constructor."""
        self.rsinstrument = False
        super().__init__(gpib, ip_address, usb, wireless, False)
        self.is_multichannel = True
        self.supports_delay = True

    def on(self, channel: str = "ALL") -> None:
        """Turn on."""
        if channel == "ALL":
            self._write("OUTPUT:STATE 1, (@1:3)")
        elif channel == 1:
            self._write("OUTPUT:STATE 1, (@1)")
        elif channel == 2:
            self._write("OUTPUT:STATE 1, (@2)")
        elif channel == 3:
            self._write("OUTPUT:STATE 1, (@3)")
        else:
            self._write("OUTPUT:STATE 1, (@%s)" % channel)

    def off(self, channel: str = "ALL") -> None:
        """Turn off."""
        if channel == "ALL":
            self._write("OUTPUT:STATE 0, (@1:3)")
        elif channel == 1:
            self._write("OUTPUT:STATE 0, (@1)")
        elif channel == 2:
            self._write("OUTPUT:STATE 0, (@2)")
        elif channel == 3:
            self._write("OUTPUT:STATE 0, (@3)")
        else:
            self._write("OUTPUT:STATE 0, (@%s)" % channel)

    def set_voltage(self, voltage: float = 1.0, channel: int = 1) -> None:
        """Set voltage."""
        self._write("VOLT %f,(@%s)" % (voltage, channel))

    def get_voltage(self, channel: int) -> float:
        """Get power supply voltage."""
        current: str = self._query(f"meas:voltage? (@{channel})")
        current_: float = float(current)
        return current_

    def set_current(
        self,
        channel: int = 1,
        current: float = 0.5,
    ) -> None:
        """Set current."""
        self._write("CURR %f,(@%s)" % (current, channel))

    def get_current(self, channel: int) -> float:
        """Read current draw from PS.

        Args:
            channel: Channel to read from.

        Returns:
            Current draw in Amps.
        """
        # Read Back the current from the power supply either in 6V mode or 25 V mode
        current: str = self._query(f"meas:curr? (@{channel})")
        current_: float = float(current)
        return current_

    def lock_front_panel(self) -> None:
        """Locks front panel to prevent changing the device settings."""
        self._write("SYSTem:RWLock")

    def unlock_front_panel(self) -> None:
        """Unlocks front panel to allow changing the device settings."""
        self._write("SYSTem:LOCal")

    def enable_ovp(self, channel: int = 1) -> None:
        """Enables OVP for the specified channel.

        :param channel: Channel to enable OVP for
        """
        self._write(f"VOLTage:PROTection ON, (@{channel})")

    def disable_ovp(self, channel: int = 1) -> None:
        """Disables OVP for the specified channel.

        :param channel: Channel to disable OVP for
        """
        self._write(f"VOLTage:PROTection OFF, (@{channel})")

    def set_ovp(self, voltage: float, channel: int = 1) -> None:
        """Sets Over Voltage Protection on PS for the specified channel.

        :param voltage: Voltage to set OVP to trigger at
        :param channel: Channel to set OVP for
        """
        self._write(f"VOLTage:PROTection {voltage}, (@{channel})")

    def clear_ovp(self, channel: int = 1) -> None:
        """Clears Over Voltage Protection for specified channel.

        :param channel: Channel to clear OVP for
        """
        self._write(f"VOLTage:PROTection:CLEar, (@{channel})")

    def is_ovp_tripped(self) -> bool:
        """Determines if Over Voltage Protection is tripped.

        :return: True if OVP is tripped, False if not
        """
        return bool(int(self._query("VOLTage:PROTection:TRIPped?")))

    def enable_ocp(self, channel: int) -> None:
        """Enables Over Current Protection for the specified channel.

        :param channel: Channel to enable OCP for
        """
        self._write(f"CURRent:PROTection:STATe ON, (@{channel})")

    def disable_ocp(self, channel: int) -> None:
        """Disables Over Current Protection for the specified channel.

        :param channel: Channel to disable OCP for
        """
        self._write(f"Current:PROTection:STATe OFF, (@{channel})")

    def clear_ocp(self, channel: int) -> None:
        """Clears Over Current Protection for the specified channel.

        :param channel: Channel to clear OCP for
        """
        self._write(f"CURRent:PROTection:CLEar, (@{channel})")

    def set_ocp_time(self, channel: int, time: float | None) -> None:
        """Sets Over Current Protection time for the specified channel.

        :param channel: Channel to set OCP time for
        :param time: Time until triggering OCP, sets to Min if time is None
        """
        self._write(
            f"CURRent:PROTection:DELay {time if time is not None else 'MINimum'}, (@{channel})"
        )

    def is_ocp_tripped(self) -> bool:
        """Determines if Over Current Protection is tripped.

        :return: True if OCP is tripped, False if not
        """
        return bool(int(self._query("CURRent:PROTection:TRIPped?")))

    def enable_voltage_sense(self, channel: int, external: bool) -> None:
        """Enables voltage sense to internal if True else external.

        :param channel: Channel to enable voltage sense for
        :param external: Flag for sense, external if True, internal if False
        """
        self._write(f"VOLTage:SENSe {'EXTernal' if external else 'INTernal'}, (@{channel})")

    def set_turn_on_delay(self, channel: int, delay: float) -> None:
        """Sets turn on delay for the specified channel.

        :param channel: Channel to set ramp up for
        :param delay: Time to delay turning on the specified channel
        """
        self._write(f"OUTP:DEL:RISE {delay}, (@{channel})")

    def set_turn_off_delay(self, channel: int, delay: float) -> None:
        """Sets turn off delay for the specified channel.

        :param channel: Channel to set ramp downfor
        :param delay: Time to delay turning off the specified channel.
        """
        self._write(f"OUTPUT:DEL:FALL {delay}, (@{channel})")

    def reset(self) -> None:
        """Reset the voltage of the power supply."""
        self._write("*RST")

    def clear_error(self) -> None:
        """Clear errors."""
        self._write("*CLS")

    def is_error(self) -> float:
        """Check the instrument to see if it has any errors in its queue."""
        raw_error = ""
        error_code: float = -1

        while error_code != 0:
            self._write("SYSTem:ERRor?; *OPC?")
            raw_error = self._read()

            error_parts = raw_error.split(",")
            error_code = int(error_parts[0])
            error_message = error_parts[1].rstrip("\n")
            print(str(error_code))  # noqa: T201
            if error_code != 0:
                print(  # noqa: T201
                    "INSTRUMENT ERROR - Error code: %d, error message: %s"
                    % (error_code, error_message)
                )

        # Clear the event status registers and empty the error queue
        self._write("*CLS")
        return error_code
