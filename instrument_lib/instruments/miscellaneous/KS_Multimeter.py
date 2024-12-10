"""Keysight 34401A Multimeter module."""

from typing import List, Optional, cast

from instrument_lib.utils import GPIBNumber
from instrument_lib.instruments.instrument import SCPIInstrument


class KS_Multimeter(SCPIInstrument):
    """Class for the Keysight 34401A Multimeter."""

    ACCEPTED_MODELS = [
        "34401A",
    ]

    def __init__(
        self,
        gpib: GPIBNumber | None = None,
        simulate: bool = False,
    ):
        """Constructor.

        :param gpib: GPIB number.
        :param wireless: wireless.
        """
        self.rsinstrument = False
        super().__init__(gpib=gpib, simulate=simulate)

    def configure_dc_reading_range(self, upper_bound: float, lower_bound: float) -> None:
        """Configures Multimeter for DC Reading with a range of the upper bound and lower bound.

        Args:
            upper_bound: The upper bound of the DC reading range.
            lower_bound: The lower bound of the DC reading range.
        """
        command_str: str = f"CONF:VOLT:DC {upper_bound}, {lower_bound}"
        self._write(command_str)

    def read_dc_voltage_measurement(self) -> float:
        """Reads current DC voltage measurement from Multimeter.

        Returns:
            A float value of the read DC voltage.
        """
        command_str: str = "MEAS:VOLT:DC?"
        read_voltage: float = float(self._query(command_str))
        return read_voltage
