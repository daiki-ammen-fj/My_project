"""Instrument Driver for RS_FSx."""

import logging
from time import sleep
from typing import Any, Optional, Tuple, Union, Callable

from instrument_lib.utils import InputSelection, SelectionState
from instrument_lib.utils import GPIBNumber
from instrument_lib.instruments.instrument import SCPIInstrument


logger = logging.getLogger(__name__)


class RS_FSx(SCPIInstrument):  # noqa
    """Spectrum Analyzer class for RS_FSx.

    All operations within this class can raise InstrumentError (or a subclass).
    """

    ACCEPTED_MODELS = [
        "FSW-85",
        "FSW-67",
        "FSWP-26",
        "FSVA3050",
    ]

    DEFAULT_SELECTION_STATE = SelectionState(False)
    INPUT_1 = InputSelection(1)
    INPUT_2 = InputSelection(2)

    def __init__(
        self,
        gpib: GPIBNumber | None = None,
        ip_address: str | None = None,
        usb: tuple[str, str, str] | None = None,
        wireless: bool = False,
        simulate: bool = False,
        retry: int = 10,
    ):
        """Constructor.

        :param gpib: Gpib number, [1, 31].
        :param ip_address: IP Address as string.
        :param wireless: Flag for wireless instrument.
        :param simulate: Flag to simulate in instrument.
        :param retry: Number of times to retry certain commands.
        """
        self.simulate = simulate
        self.rsinstrument = True
        self.retry: int = retry
        super().__init__(gpib, ip_address, usb, wireless, simulate)

    def __str__(self) -> str:
        """String representation of this class."""
        return "Spectrum Analyzer: RS_FSx"

    def retry_on_failure(function: Callable) -> Callable:  # type: ignore # noqa
        """Docstring."""

        def wrapper(self, *args: int, **kwargs: int) -> None:  # noqa
            failures: int = 0
            while failures <= self.retry:
                try:
                    return function(self, *args, **kwargs)
                except Exception:
                    failures += 1

        return wrapper

    def display(self, select: SelectionState = DEFAULT_SELECTION_STATE) -> None:
        """Toggle Display on/off while remote.

        Args:
            select: On/Off selection state. Defaults to DEFAULT_SELECTION_STATE.
        """
        logger.debug(f"Toggling display with selection state: {select}")
        self._write(f"SYSTem:DISPlay:UPDate {select}")

    def run_continuous(self, select: SelectionState = DEFAULT_SELECTION_STATE) -> None:
        """TODO: Add docstring."""
        self._write(f":INIT:CONT {select}")

    def set_freq(self, freq: float = 30e9) -> None:
        """Set Center Frequency.

        Args:
            freq: Frequency in Hertz (Hz). Defaults to 30e9.
        """
        logger.info(f"Setting center frequency to {freq} Hz")
        self._write(f":FREQuency:CENT {freq} HZ")
        self.freq = freq

    def get_freq(self) -> float:
        """Gets freq in Hz."""
        logger.debug("Fetching current center frequency.")
        self.freq = float(self._query(":FREQuency:CENT?"))
        logger.debug(f"Current center frequency => {self.freq}")
        return self.freq

    def set_span(self, span: float = 2e6) -> None:
        """Set frequency span.

        Args:
            span: Span range in Hertz. Defaults to 2e6.
        """
        logger.info(f"Setting frequency span to {span} Hz")
        self._write(f":FREQ:SPAN {span} HZ")

    def get_span(self) -> float:
        """Gets freq in Hz."""
        logger.debug("Fetching current frequency span.")
        self.span = float(self._query(":FREQuency:CENT?"))
        logger.debug(f"Current frequency span => {self.span}")
        return self.freq

    def set_rbw(self, rbw: float = 100e3) -> None:
        """Set the resolution bandwidth.

        Args:
            rbw: Resolution bandwidth in Hertz. Defaults to 100e3.
        """
        logger.info(f"Setting RBW to {rbw} Hz")
        self._write(f":BAND {rbw} HZ")

    def set_ref(self, ref: float = 0) -> None:
        """Sets the reference power level."""
        logger.info(f"Setting reference power level to {ref} dBm")
        self._write(f":DISP:WIND:TRAC:Y:RLEV {ref} DBM")

    def set_vbw(self, vbw: float = 50) -> None:
        """Sets the VBW."""
        logger.info(f"Setting VBW to {vbw}")
        self._write(f"SENS:BAND:VID {vbw}")

    @retry_on_failure
    def get_peak(self) -> Tuple[float, float]:
        """Gets the peak information (frequency and amplitude)."""
        logger.info("Retrieving peak information.")
        self._write(":CALC1:MARK1:MAX:PEAK")
        amplitude = self.get_y()
        frequency = self.get_x()
        logger.debug(f"Peak found at Frequency: {frequency} Hz, Amplitude: {amplitude} dBm")
        return amplitude, frequency

    @retry_on_failure
    def get_y(self) -> float:
        """Gets the amplitude (y value) of the marker."""
        logger.debug("Fetching amplitude of the marker.")
        amplitude = self._query(":CALC:MARK1:Y?") if not self.simulate else "0"
        logger.debug(f"Marker amplitude: {amplitude} dBm")
        return float(amplitude)

    @retry_on_failure
    def get_x(self) -> float:
        """Gets the frequency (x value) of the marker."""
        logger.debug("Fetching frequency of the marker.")
        frequency = self._query(":CALC:MARK1:X?") if not self.simulate else "0"
        logger.debug(f"Marker frequency: {frequency} Hz")
        return float(frequency)

    def set_input_type(self, input_selection: InputSelection = INPUT_2) -> None:
        """Sets input type."""
        logger.info(f"Setting input type to {input_selection}")
        self._write(f":INP:TYPE {input_selection}")

    def get_channel_power(self) -> float:
        """Gets the channel power."""
        logger.info("Retrieving channel power.")
        self._write("SYSTem:SEQuencer ON")
        self._write("INITiate:SEQuencer:MODE SINGle")
        self._write("INITiate:SEQuencer:IMMediate;*OPC?")
        power = (
            self._query("CALCulate:MARKer:FUNCtion:POWer:RESult? CPOWer")
            if not self.simulate
            else "0"
        )
        logger.debug(f"Channel power: {power} dBm")
        return float(power)

    def setup_spectrum(self, center_freq: float, span: float, markers: list[float]) -> None:
        """Setup Spectrum Analyzer Tab."""
        logger.info(
            f"Setting up spectrum with center frequency: {center_freq} Hz, span: {span} Hz, markers: {markers}"
        )
        self._write("INST:SEL SAN")
        self._write(":INIT:CONT OFF")
        self._write(f":SENS:FREQ:CENT {center_freq}")
        self._write(f":SENS:FREQ:SPAN {span}")
        self._write(":SENS:BAND:RES 1000000")
        self._write(":SENS:BAND:VID 50000")
        self._write(":DISP:WIND1:SUBW:TRAC1:Y:RLEV -30")
        self._write(":DISP:WIND1:SUBW:TRAC1:Y:SCAL:AUTO ONCE")

        for marker, freq in enumerate(markers):
            logger.debug(f"Setting marker {marker+1} at frequency {freq} Hz")
            self._write(f":CALC1:MARK{marker+1}:STAT ON")
            self._write(f":CALC1:MARK{marker+1}:X {freq}")
        self._write(":INIT:CONT ON")

    def setup_acp(
        self, num_channels: int, channel_bw: int, channel_spacing: int, tab_name: str = "ACP"
    ) -> None:
        """Setup ACP Tab.

        Args:
            num_channels: Number of TX channels.
            channel_bw: Channel bandwidth
            channel_spacing: Channel spacing
            tab_name: Display name. Defaults to "ACP".
        """
        self._write(f"INST:CRE:NEW SANALYZER, '{tab_name}'")
        self._write(":INIT:CONT OFF")
        self._write(":CALC1:MARK:FUNC:POW:SEL ACP")
        self._write(f":SENS:POW:ACH:TXCH:COUN {num_channels}")
        self._write(f":SENS:POW:ACH:TXCH:BWID:CHAN1 {int(channel_bw)}")
        self._write(f":SENS:POW:ACH:TXCH:SPAC:CHAN1 {int(channel_spacing)}")
        self._write(":SENS:BAND:RES 20000")
        self._write(":SENS:BAND:VID 50000")
        self._write(":DISP:WIND:SUBW:TRAC:Y:SPAC LOG")
        self._write(":DISP:WIND:SUBW:TRAC:Y:SCAL 60")
        self._write(":DISP:WIND:TRAC:Y:SCAL:RLEV -30")

    def evm_setup_5gnr(self, frequency: float, waveform: str, tab_name: str = "5G NR") -> None:
        """Setup 5G NR mode with specific waveform file.

        Args:
            frequency: RF Frequency in Hertz (Hz).
            waveform: Waveform filename.
            tab_name: Tab display name. Defaults to "5G NR".
        """
        try:
            self._write(f"INST:SEL '{tab_name}'")
        except Exception as e:
            logger.warning(f"Could not find tab '{tab_name}' dut to {str(e)}. Creating new tab.")
            self._write(f":INST:CRE:NEW NR5G, '{tab_name}'")
        self._write(":INIT:CONT ON")
        self._write(f":MMEM:LOAD:TMOD:CC1 '{waveform}'")
        self._write(":CONF:NR5G:DL:CC1:IDC ON")
        self._write(":SENS:NR5G:DEM:EFLR ON")
        self._write(":SYST:DISP:UPD ON")
        self._write(f":SENS:FREQ:CENT {frequency}")
        self._write(":CONF:NR5G:DL:CC1:RFUC:STAT ON")
        self._write(":CONF:NR5G:DL:CC1:RFUC:FZER:MODE MAN")
        self._write(f":CONF:NR5G:DL:CC1:RFUC:FZER:FREQ {frequency} HZ")
        self._write(":SENS:ADJ:EVM;*WAI")
        sleep(0.5)
        self._write(":INIT:CONT ON")

    def set_phase_compensation_frequency(self, phase_comp_frequency: float) -> None:
        """Set phase compensation frequency.

        :param phase_comp_frequency: Frequency of phase compensation.
        """
        self._write(":CONF:NR5G:DL:CC1:RFUC:STAT ON")
        sleep(0.1)
        self._write(":CONF:NR5G:DL:CC1:RFUC:FZER:MODE MAN")
        self._write(f":CONF:NR5G:DL:CC1:RFUC:FZER:FREQ {phase_comp_frequency} HZ")

    def get_evm(self) -> float:
        """Gets EVM.

        :return: EVM value.
        """
        self._write(":INIT:IMM;*WAI")
        if not self.simulate:
            evm: Union[str, Any] = self._query("FETCh:CC1:ISRC:FRAM:SUMMary:EVM:DSTS:AVER?")
        else:
            evm = 0

        return float(evm)

    def get_evm_power(self) -> float:
        """Gets EVM power.

        :return: EVM Power Value.
        """
        if not self.simulate:
            evm_power: Union[str, Any] = self._query("FETCh:CC1:ISRC:FRAM:SUMMary:Power:AVER?")
        else:
            evm_power = 0

        return float(evm_power)

    def get_jitter_fswp(self, num: int) -> float:
        """Gets the residual RMS jitter from the selected range.

        :param num: Integration Range number

        :return: Residual Jitter (s)
        """
        jitter: str = self._query(f"FETC:RANG{num}:PNO:RMS?")
        return float(jitter)

    def get_int_noise_fswp(self, num: int) -> float:
        """Gets the integrated phase noise from the selected range.

        :param num: Integration Range number

        :return: Integrated Noise (dBc)
        """
        noise: str = self._query(f"FETC:RANG{num}:PNO:IPN?")
        return float(noise)

    def get_freq_fswp(self) -> float:
        """Gets the center frequency value from the fswp.

        :return: Center Frequency (Hz)
        """
        signal_frequency: str = self._query("FREQ:CENT?")
        return float(signal_frequency)

    def get_spot_noise_fswp(self, num: int) -> float:
        """Gets the spot noise from the selected spot noise marker.

        :param num: Spot Noise Marker

        :return: Phase noise level at the spot noise position (dBc/Hz)
        """
        spot: str = self._query(f"CALC:SNO{num}:Y?")
        return float(spot)

    def get_power_fswp(self) -> float:
        """Gets the measured signal level from the fswp.

        :return: Signal level (dBm)
        """
        signal_level: str = self._query("POW:RLEV?")
        return float(signal_level)

    def run_single_fswp(self) -> None:
        """Runs a single measurement."""
        self._write("INIT:IMM")

    def get_single_time_fswp(self) -> float:
        """Gets the time value it takes to run a single measurement from the fswp.

        :return: Single measurement runtime (s)
        """
        runtime: str = self._query("SENS:SWE:TIME?")
        return float(runtime)

    def toggle_signal_source_output_fswp(
        self, select: SelectionState = DEFAULT_SELECTION_STATE
    ) -> None:
        """Turns the signal source output on and off.

        Args:
            select: Toggle On/Off. Defaults to DEFAULT_SELECTION_STATE, a value of OFF. Options are SelectionState(True) or SelectionState(False).
        """
        self._write(f":SOUR:GEN:STAT {select.get_state()}")

    def set_signal_source_freq_fswp(self, freq: float = 122.88) -> None:
        """Sets the frequency of the signal that is generated by the signal source.

        Args:
            freq: Frequency in MHz. Defaults to 122.88.
        """
        self._write(f":SOUR:GEN:FREQ {freq*1000000}")

    def set_signal_source_power_fswp(self, power_level: int = 0) -> None:
        """Sets the level of the signal that is generated by the signal source.

        Args:
            power_level: Signal level in dBm. Defaults to 0.
        """
        self._write(f":SOUR:GEN:LEV {power_level}")

    def set_default_signal_source_config_fswp(self) -> None:
        """Turns on the input signal source to 122.88MHz @ 0dBm."""
        self.set_signal_source_freq_fswp(freq=122.88)
        self.set_signal_source_power_fswp(power_level=0)
        self.toggle_signal_source_output_fswp(select=SelectionState(True))

    def set_lo_spectrum_analyzer_config_fswp(
        self, with_x4: bool = True, reset_fswp: bool = True
    ) -> None:
        """Sets the Spectrum Analyzer Tab for LO Synth testing.

        Args:
            with_x4: Sets the frequency span according to pre/post x4 boolean condition, 4-7GHz or 20-25GHz. Defaults to True.
            reset_fswp: Resets the FSWP to fresh bringup, all tabs get deleted. Defaults to True.
        """
        if with_x4:
            freq_start = 20000000000
            freq_stop = 25000000000
        else:
            freq_start = 4500000000
            freq_stop = 6500000000

        if reset_fswp:
            self._write("*RST")
            self._write("*CLS")
            self._write(":SYST:DISP:UPD ON")
            self._write(":INIT:CONT OFF")
        self._write(":INST:CRE:NEW SAN, 'SAN LO Synth Test'")
        self._write(f":SENS:FREQ:STAR {freq_start}")
        self._write(f":SENS:FREQ:STOP {freq_stop}")
        self._write(":INP:ATT:AUTO OFF")
        self._write(":INP:ATT 0")

    def set_lo_phase_noise_config_fswp(
        self, with_x4: bool = True, reset_fswp: bool = False
    ) -> None:
        """Sets the Phase Noise Tab for LO Synth testing.

        Args:
            with_x4: Sets the frequency span according to pre/post x4 boolean condition, 4-7GHz or 20-25GHz. Defaults to True.
            reset_fswp: Resets the FSWP to fresh bringup, all tabs get deleted. Defaults to False.
        """
        if with_x4:
            freq_start = 20000000000
            freq_stop = 25000000000
        else:
            freq_start = 4500000000
            freq_stop = 6500000000

        if reset_fswp:
            self._write("*RST")
            self._write("*CLS")
            self._write(":SYST:DISP:UPD ON")
            self._write(":INIT:CONT OFF")
        self._write(":INST:CRE:NEW PNO, 'PNO LO Synth Test'")
        self._write(":INIT:CONT OFF")
        self._write(":INP:ATT:AUTO OFF")
        self._write(":INP:ATT 0")
        # self._write(":INP:ATT:AUTO ON") # FIXME Decide if attenuation should be automatic or manual
        self._write(f":SENS:ADJ:CONF:FREQ:LIM:LOW {freq_start}")
        self._write(f":SENS:ADJ:CONF:FREQ:LIM:HIGH {freq_stop}")
        self._write(":SENS:ADJ:CONF:LEV:THR -35")
        self._write(":SENS:SWE:CAPT:RANG WIDE")
        self._write(":SENS:FREQ:STOP 1000000000")
        self._write(":SENS:LIST:BWID:RES:USM ON")
        self._write(":SENS:SWE:XFAC 100")
        self._write(":SENS:SWE:COUN 1")
        self._write(":CALC1:RANG1:EVAL:STAT OFF")
        self._write(":CALC1:RANG2:EVAL:STAT OFF")
        self._write(":CALC1:RANG3:EVAL:STAT OFF")
        self._write(":CALC1:RANG2:EVAL:TRAC TRACE1")
        self._write(":CALC1:RANG3:EVAL:TRAC TRACE1")
        self._write(":CALC1:RANG1:EVAL:STAR 12000")
        self._write(":CALC1:RANG2:EVAL:STAR 12000")
        self._write(":CALC1:RANG3:EVAL:STAR 12000")
        self._write(":CALC1:RANG1:EVAL:STOP 20000000")
        self._write(":CALC1:RANG2:EVAL:STOP 200000000")
        self._write(":CALC1:RANG3:EVAL:STOP 400000000")
        self._write(":CALC:SNO:TRAC:DEC:STAT OFF")
        self._write(":CALC1:SNO1:X 12000")
        self._write(":CALC1:SNO2:X 100000")
        self._write(":CALC1:SNO3:X 1000000")
        self._write(":CALC1:SNO4:X 10000000")
        self._write(":CALC1:SNO5:X 100000000")
        self._write(":CALC1:SNO6:X 200000000")

    def run_lo_startup(self, with_x4: bool = True, input_signal: bool = True) -> None:
        """Sets the Phase Noise Tab for LO Synth testing.

        Args:
            with_x4: Sets the frequency span according to pre/post x4 boolean condition, 4-7GHz or 20-25GHz. Defaults to True.
            input_signal: If true, turns on the input signal source to 122.88MHz @ 0dBm. Defaults to True.
        """
        self.set_lo_spectrum_analyzer_config_fswp(with_x4=with_x4, reset_fswp=True)
        self.set_lo_phase_noise_config_fswp(with_x4=with_x4, reset_fswp=False)
        if input_signal:
            self.set_default_signal_source_config_fswp()

    def get_frontend_temp(self) -> float:
        """Gets the current temperature of the frontend sensor for the FSW/FSWP.

        :return: Temperature in degrees (Celsius).
        """
        temp: str = self._query("SOUR:TEMP:FRON?")
        return float(temp)

    def get_exact_peak(self, freq: float) -> tuple[float, float]:
        """Get the exact frequency up to 9 decimals points in GHz, & the amplitude. Uses a span of 1kHz.

        Args:
            freq: Rough input frequency in GHz. Input can be up to 0.5GHz off, since starting span is 1GHz.

        Returns:
            Tuple of amplitude and frequency(up to 9 decimal point accuracy).
        """
        self.set_freq(freq * 1e9)
        self.set_span(1000000000)
        sleep(0.3)
        self.set_freq(self.get_peak()[1])
        self.set_span(10000000)
        sleep(0.3)
        self.set_freq(self.get_peak()[1])
        self.set_span(1000000)
        sleep(0.3)
        self.set_freq(self.get_peak()[1])
        self.set_span(10000)
        sleep(0.4)
        self.set_freq(self.get_peak()[1])
        self.set_span(1000)
        sleep(1)
        return self.get_peak()
