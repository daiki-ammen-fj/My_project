"""Instrument Driver for RS_SMx."""

from time import sleep
from typing import Optional

from instrument_lib.utils import GPIBNumber, SelectionState
from instrument_lib.instruments.instrument import SCPIInstrument


class RS_SMx(SCPIInstrument):  # noqa
    """Signal Generator class for RS_SMx.

    All operations within this class can raise InstrumentError (or a subclass).
    """

    ACCEPTED_MODELS = [
        "SMW200A",
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
        self.rsinstrument = True

    def __str__(self) -> str:
        """String representation of this class."""
        return "IF Signal Generator: RS_SMx"

    def reset(self) -> None:
        """Reset signal generator."""
        self._write("*CLS")
        self._write(":SYST:DISP:UPD ON")
        self._write("*RST")
        self._write(":INIT:CONT OFF")

    def load_waveform(self, waveform: str, source: int = 1) -> None:
        """Load ARB Waveform (Arbitrary).

        :param waveform: Path to waveform file.
        :param source: Input source number. Defaults to 1.
        """
        self._write(f'SOURce{source}:BB::ARBitrary:WAVeform:SELect "{waveform}"')
        self._write(f"SOURce{source}:BB:ARBitrary:STATe 1")
        self._write(f"SOURce{source}:BB:ARBitrary:STATe 1")

    def load_5gnr_model(self, waveform: str, source: int = 1) -> None:
        """Load 5G NR Test model.

        Args:
            waveform: Test model filename.
            source: Source input number. Defaults to 1.
        """
        self._write(f'SOURce{source}:BB:NR5G:SETTing:TMODel:DL "{waveform}"')
        self._write(f"SOURce{source}:BB:NR5G:STATe 0")
        self._write(f"SOURce{source}:BB:NR5G:STATe 1")

    def set_phase_compensation(self, phase_compensation_frequency: float, source: int = 1) -> None:
        """Set Phase compensation frequency for reference.

        Args:
            phase_compensation_frequency: Frequency in Hertz (Hz)
            source: Source input number. Defaults to 1.
        """
        self._write(f"SOURce{source}:BB:NR5G:NODE:RFPHase:MODE MAN")
        self._write(f"SOURce{source}:BB:NR5G:NODE:CELL0:PCFReq {phase_compensation_frequency}")

    def set_freq(self, freq: float = 3e9, source: int = 1) -> None:
        """Sets the center frequency.

        :param freq: Signal frequency in Hz. Defaults to 3e9.
        :param source: Input source number. Defaults to 1.
        """
        self._write(f":SOURce{source}:FREQuency {freq} HZ")
        self.freq = freq

    def get_freq(self) -> float:
        """Gets freq in Hz.

        :return: freq
        """
        return self.freq

    def set_amplitude(self, amplitude: float = -30, source: int = 1) -> None:
        """Sets amplitude (power level).

        :param amplitude: Amplitude (power level). Defaults to -30.
        :param source: Input source number. Defaults to 1.
        """
        self.set_power_level(amplitude, source)

    def set_span(self, span: float = 2e6) -> None:
        """Set the frequency span.

        :param span: Frequency span range. Defaults to 2e6.
        """
        self._write(f":FREQ:SPAN {span} HZ")

    def set_power_limit(self, power: float = 10, source: int = 1) -> None:
        """PEP power limit.

        :param power: Power level limit in dbm. Defaults to 10.
        :param source: Input source number. Defaults to 1.
        """
        self._write(f":SOURce{source}:POWer:LIMit:AMPlitude {power}")

    def get_power(self) -> float:
        """Gets power level in dbm.

        :return: Power level
        """
        return self.power

    def set_power_level(self, power: float = -30, source: int = 1) -> None:
        """Set power level on defined source.

        :param power: Power level in dbm. Defaults to -30.
        :param source: Input source number. Defaults to 1.
        """
        self._write(f":SOURce{source}:POWer:Immediate:AMPLitude {power}")
        self.power = power

    def set_reference_power_level(self, reference_level: float = 0) -> None:
        """Sets reference power level.

        :param reference_level: Reference level. Defaults to 0.
        """
        self._write(f":DISP:WIND:TRAC:Y:RLEV {reference_level} DBM")

    def mod_switch(self, selection: SelectionState = DEFAULT_SELECTION_STATE) -> None:
        """Modulation switch  -> Enables/disables the I/Q Modulation.

        :param selection: Select state (on or off). Defaults to OFF.
        """
        self._write(f":SOURce:IQ:STAT {selection.get_state()}")

    def rf_switch(self, selection: SelectionState = DEFAULT_SELECTION_STATE) -> None:
        """RF Switch.

        :param selection: Select state (on or off). Defaults to OFF.
        """
        self._write(f"OUTP:STAT {selection.get_state()}")

    def output_trigger_setup(self, source: int = 1) -> None:
        """# TODO: Add docstring.

        :param source: Input source number. Defaults to 1.
        """
        self._write(f"SOURce{source}:INPut:USER6:DIRection OUTP")

    def output_trigger(self, width: float = 0.001, source: int = 1) -> None:
        """# TODO: Add docstring.

        :param witdh: [description]. Defaults to 1.
        :param source: Input source number. Defaults to 1.
        """
        self._write(f"OUTPut{source}USER6:SIGNal HIGH")
        sleep(width)  # TODO: Find alternative to sleep.
        self._write(f"OUTPut{source}:USER6:SIGNal LOW")

    def set_trigger_high(self, source: int = 1) -> None:
        """Sets trigger high.

        :param source: Input source number. Defaults to 1.
        """
        self._write(f"OUTPut{source}:USER6:SIGNal HIGH")

    def set_trigger_low(self, source: int = 1) -> None:
        """Sets trigger low.

        :param source: Input source number. Defaults to 1.
        """
        self._write(f"OUTPut{source}:USER6:SIGNal LOW")
