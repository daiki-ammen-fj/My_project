"""Instrument driver for E36102B_PS."""

from typing import Optional
from instrument_lib.utils import GPIBNumber
from instrument_lib.instruments.instrument import SCPIInstrument


class KS_E36100_PS(SCPIInstrument):  # noqa: N801
    """KS_E36100_PS class."""

    ACCEPTED_MODELS = [
        "E36102B",
        "E36103B",
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
        self.is_multichannel = False
        self.supports_delay = False

    def on(self, channel: str = "ALL") -> None:
        """Turn on."""
        self._write("OUTPUT:STATE 1")

    def off(self, channel: str = "ALL") -> None:
        """Turn off."""
        self._write("OUTPUT:STATE 0")

    def set_voltage(self, voltage: float = 1.0, channel: int = 1) -> None:
        """Set voltage."""
        self._write(f"VOLT {voltage}")

    def set_current(self, channel: int = 1, current: float = 0.5) -> None:
        """Set current."""
        self._write(f"CURR {current}")

    def get_current(self, channel: Optional[int]) -> float:
        """Read current draw from PS.

        Args:
            channel: Channel to read from. Unused.

        Returns:
            Current draw in Amps.
        """
        current: str = self._query("meas:curr?")
        current_: float = float(current)
        return current_

    def get_voltage(self, channel: Optional[int]) -> float:
        """Get voltage."""
        voltage: str = self._query("meas:volt?")
        voltage_: float = float(voltage)
        return voltage_

    def lock_front_panel(self) -> None:
        """Locks front panel to prevent changing the device settings."""
        self._write("SYSTem:RWLock")

    def unlock_front_panel(self) -> None:
        """Unlocks front panel to allow changing the device settings."""
        self._write("SYSTem:LOCal")

    def enable_ovp(self) -> None:
        """Enables OVP for the specified channel."""
        self._write("VOLTage:PROTection:STATe ON")

    def disable_ovp(self) -> None:
        """Disables OVP for the specified channel."""
        self._write("VOLTage:PROTection:STATe OFF")

    def set_ovp(self, voltage: float) -> None:
        """Sets Over Voltage Protection on PS.

        :param voltage: Voltage to set OVP to trigger at
        """
        self._write(f"VOLTage:PROTection {voltage}")

    def clear_ovp(self) -> None:
        """Clears Over Voltage Protection."""
        self._write("VOLTage:PROTection:CLEar")

    def is_ovp_tripped(self) -> bool:
        """Determines if Over Voltage Protection is tripped.

        :return: True if OVP is tripped, False if not
        """
        return bool(int(self._query("VOLTage:PROTection:TRIPped?")))

    def enable_ocp(self) -> None:
        """Enables Over Current Protection."""
        self._write("CURRent:PROTection:STATe ON")

    def disable_ocp(self) -> None:
        """Disables Over Current Protection for the specified channel."""
        self._write("Current:PROTection:STATe OFF")

    def clear_ocp(self) -> None:
        """Clears Over Current Protection."""
        self._write("CURRent:PROTection:CLEar")

    def set_ocp_time(self, time: float | None) -> None:
        """Sets Over Current Protection time.

        :param time: Time until triggering OCP, sets to Min if time is None
        """
        self._write(f"CURRent:PROTection:DELay {time if time is not None else 'MINimum'}")

    def is_ocp_tripped(self) -> bool:
        """Determines if Over Current Protection is tripped.

        :return: True if OCP is tripped, False if not
        """
        return bool(int(self._query("CURRent:PROTection:TRIPped?")))

    def enable_voltage_sense(self, external: bool) -> None:
        """Enables voltage sense to internal if True else external.

        :param external: Flag for sense, external if True, internal if False
        """
        self._write(f"VOLTage:SENSe {'EXTernal' if external else 'INTernal'}")

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
