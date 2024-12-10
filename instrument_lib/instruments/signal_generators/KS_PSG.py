"""Instrument Driver for KS_PSG."""

from typing import Optional

from instrument_lib.utils import SelectionState
from instrument_lib.utils.gpib_number import GPIBNumber
from instrument_lib.instruments.instrument import SCPIInstrument


class KS_PSG(SCPIInstrument):
    """Signal Generator class for this device.

    All operations within this class can raise InstrumentError (or a subclass).
    """

    ACCEPTED_MODELS = [
        "E8257D",
        "E8267D",
        "E8663D",
    ]

    DEFAULT_SELECTION_STATE = SelectionState(False)

    def __init__(
        self,
        gpib: GPIBNumber | None = None,
        ip_address: str | None = None,
        usb: tuple[str, str, str] | None = None,
        wireless: bool = False,
        simulate: bool = False,
    ):
        """Constructor.

        :param gpib: Gpib number, [1, 31].
        :param ip_address: IP Address as string.
        :param wireless: Flag for wireless instrument.
        :param simulate: Flag to simulate in instrument.
        """
        super().__init__(gpib, ip_address, usb, wireless, simulate)
        self.freq: float = 0
        self.power: float = 0
        self.rsinstrument = False

    def get_power(self) -> float:
        """Gets power level in dbm.

        :return: Power level
        """
        return self.power

    def set_freq(self, freq: float = 30e9) -> None:
        """Sets the center frequency.

        :param freq: Signal frequency in Hz. Defaults to 30e9.
        :param source: Input source number. Defaults to 1.
        """
        self._write(f":FREQ:CW {freq} HZ")
        self.freq = freq

    def get_freq(self) -> float:
        """Gets freq in Hz.

        :return: freq
        """
        self._write(":FREQ:CW?")
        freq = self._read()
        return float(freq)

    def set_amplitude(self, amplitude: float = -20) -> None:
        """Set amplitude (power level).

        :param amplitude: Amplitude (power level.) Defaults to -20.
        """
        self._write(f":POW:AMPL {amplitude} dBm")
        self.power = amplitude

    def get_amplitude(self) -> float:
        """Gets amplitude (power level).

        :return: Amplitude in dbm.
        """
        self._write(":POW:AMPL?")
        amplitude = self._read()
        return float(amplitude)

    def mod_switch(self, selection: SelectionState = DEFAULT_SELECTION_STATE) -> None:
        """Modulation switch  -> Enables/disables the I/Q Modulation.

        :param selection: Select state (on or off). Defaults to OFF.
        """
        self._write(f"FM:STAT {selection.get_state()}")

    def rf_switch(self, selection: SelectionState = DEFAULT_SELECTION_STATE) -> None:
        """RF Switch.

        :param selection: Select state (on or off). Defaults to OFF.
        """
        self._write(f"OUTP:STAT {selection.get_state()}")
