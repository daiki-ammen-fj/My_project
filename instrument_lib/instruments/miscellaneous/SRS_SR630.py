"""Instrument driver for SRS SR630 Thermocouple Monitor."""

from typing import Optional

from instrument_lib.utils import GPIBNumber
from instrument_lib.instruments.instrument import SCPIInstrument


class SRS_SR630(SCPIInstrument):  # noqa: N801
    """SRS_SR630 class."""

    ACCEPTED_MODELS = [
        "SR630",
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

    def get_name(self) -> str:
        """Get device identification.

        :return: Device Name
        """
        return self._query("*IDN?")

    def read_channel(self, channel: int) -> float:
        """Read channel value.

        :param channel: channel number to read

        :return: channel reading
        """
        command = "CHAN?"
        current_channel = self._query(command)
        if int(current_channel) == channel:
            command = "MEAS? " + str(channel)
            value = self._query(command)
        else:
            command = "CHAN " + str(channel)
            self._write(command)
            command = "MEAS? " + str(channel)
            value = self._query(command)
        value = value.replace("\n", "")
        return float(value)
