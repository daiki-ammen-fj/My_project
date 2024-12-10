"""Instrument driver for DC310S Power Supply."""

from typing import Optional
from instrument_lib.instruments.instrument import SCPIInstrument
from instrument_lib.utils.gpib_number import GPIBNumber


class DC310S_PS(SCPIInstrument):  # noqa: N801
    """DC310S_PS class."""

    ACCEPTED_MODELS = [
        "DC310S",
    ]

    def __init__(
        self,
        gpib: GPIBNumber | None = None,
        ip_address: str | None = None,
        usb: tuple[str, str, str] | None = None,
        wireless: bool = False,
        simulate: bool = False,
        serial_instrument_port: str | int | None = None,
        serial_instrument_baudrate: int = 115200,
    ):
        """Constructor."""
        super().__init__(
            gpib,
            ip_address,
            usb,
            wireless,
            simulate,
            serial_instrument_port,
            serial_instrument_baudrate,
        )

    def on(self) -> None:
        """Turns power supply output on."""
        self._write("OUTPut 1")

    def off(self) -> None:
        """Turns power supply output off."""
        self._write("OUTPut 0")

    def is_outputting_power(self) -> bool:
        """Checks if power supply is currently outputting power.

        :return: Output status of power supply, If power supply is active, returns 1.
        """
        ps_status: str = self._query("OUTPUt?")
        ps_status_bool: bool = bool(ps_status)
        return ps_status_bool

    def measure_voltage(self) -> float:
        """Queries the voltage measured on the output terminal of the channel.

        :return: Voltage measured on output terminal.
        """
        voltage: str = self._query("MEASure:VOLTage?")
        voltage_float: float = float(voltage)
        return voltage_float

    def measure_current(self) -> float:
        """Query the current measured on the output terminal of the channel.

        :return: Current measured on output terminal.
        """
        current: str = self._query("MEASure:CURRent?")
        current_float: float = float(current)
        return current_float

    def measure_power(self) -> float:
        """Queries the power measured on the output terminal of the channel.

        :return: Power measured on output terminal.
        """
        power: str = self._query("MEASure:POWer?")
        power_float: float = float(power)
        return power_float

    def get_voltage(self) -> float:
        """Queries voltage setting value of the channel.

        :return: Voltage setting value of channel.
        """
        voltage: str = self._query("VOLTage?")
        voltage_float: float = float(voltage)
        return voltage_float

    def get_current(self) -> float:
        """Queries current setting value of the channel.

        :return: Current setting value of channel.
        """
        current: str = self._query("CURRent?")
        current_float: float = float(current)
        return current_float

    def get_voltage_limit(self) -> float:
        """Queries current voltage limit of the channel.

        :return: Current voltage limit of channel.
        """
        voltage_limit: str = self._query("VOLTage:LIMit?")
        voltange_limit_float: float = float(voltage_limit)
        return voltange_limit_float

    def get_current_limit(self) -> float:
        """Queries current current limit of channel.

        :return: Current current limit of channel.
        """
        current_limit: str = self._query("CURRent:LIMit?")
        current_limit_float: float = float(current_limit)
        return current_limit_float

    def set_voltage(self, voltage: float) -> None:
        """Set voltage of channel.

        :param voltage: The voltage value being set.
        """
        self._write(f"VOLTage {voltage}")

    def set_current(self, current: float) -> None:
        """Set current of channel.

        :param current: The current value being set.
        """
        self._write(f"CURRent {current}")

    def set_voltage_limit(self, voltage: float) -> None:
        """Set voltage limit of channel.

        :param voltage: Voltage limit value being set.
        """
        self._write(f"VOLTage:LIMit {voltage}")

    def set_current_limit(self, current: float) -> None:
        """Set current limit of channel.

        :param current: Current limit value being set.
        """
        self._write(f"CURRent:LIMit {current}")
