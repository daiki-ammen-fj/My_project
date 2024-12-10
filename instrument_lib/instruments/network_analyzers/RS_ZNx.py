"""Instrument driver for RS_ZNx."""

import math
from typing import Any, Callable, List, Optional, Tuple, Union

import numpy as np
from numpy import floating

from instrument_lib.utils import GPIBNumber
from instrument_lib.instruments.instrument import SCPIInstrument


class RS_ZNx(SCPIInstrument):  # noqa: N801
    """ZNA driver class for this device.

    All operations within this class can raise InstrumentError (or a subclass).
    """

    ACCEPTED_MODELS = [
        "ZNA",
        "ZNA50-4Port",
        "ZNA67-4Port",
        "ZNB8-4Port",
    ]

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
        :param retry: Number of times to retry certain commands.
        """
        super().__init__(gpib, ip_address, usb, wireless, simulate)
        self.retry: int = retry
        self.rsinstrument = True

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

    def run_continuous(self) -> None:
        """Tells instrument to run continuously."""
        self._write(":INITIATE:CONTinuous:ALL ON")

    def load_recall(self, recall_filepath: str) -> None:
        """Loads recall from file.

        :param recall_filepath: Filepath of recall.
        """
        self._write(f"MMEM:LOAD:STAT 1, '{recall_filepath}'")

    def frequency_sweep_setup(
        self,
        frequency_start: float = 28e9,
        frequency_stop: float = 28e9,
        frequency_points: int = 1,
        port: int = 1,
        channel: int = 1,
    ) -> None:
        """Sets start, stop, step for Frequency sweep.

        :param frequency_start: Start Frequency (Hz)
        :param frequency_stop: Stop Frequency (Hz)
        :param frequency_steps: Frequency Steps
        :param port: RF Port
        :param channel: Instrument Channel
        """
        self._write(f"SENSe{channel}:SWEEp:POINts {frequency_points}")
        self._write(f"SENSe{channel}:FREQuency{port}:STARt {frequency_start}")
        self._write(f"SENSe{channel}:FREQuency{port}:STOP {frequency_stop}")

    def mixer_setup(
        self,
        lo_frequency: float = 20.6e9,
        if_frequency: float = 2.94912e9,
        if_power: float = -30,
    ) -> None:
        """Sets up mixer.

        :param lo_frequency: Frequency (Hz) for local ossicillator (LO)
        :param if_frequency: Frequency (Hz) for intermittent frequency (IF)
        :param if_power: Power (Watts?) for intermitted frequency (IF)
        """
        self._write("SENSe1:SWEEp:TYPE LINear")
        self._write("SENSe1:SWEEp:POINts 201")
        self._write(f"SENSe1:FREQuency1:STARt {if_frequency}")  # start : 500 MHz')
        self._write(f"SENSe1:FREQuency1:STOP {if_frequency}")  # stop : 2.5 GHz
        self._write("SOURce1:POWer1 0")  # Base power

        self._write("FREQuency:CONVersion:MIXer:IFPort 1")
        self._write("FREQuency:CONVersion:MIXer:RFPort 2")
        self._write("SENSe1:FREQuency1:CONVersion:MIXer:FIXed LO")
        self._write("SENSe1:FREQuency1:CONVersion:MIXer:FUND IF")
        self._write("SENSe1:FREQuency1:CONVersion:MIXer:LOINternal 3")  # LO port 3
        self._write("SENSe1:FREQuency1:CONVersion:MIXer:TFRequency DCLower")  # RF + LO
        self._write(f"SENSe1:FREQuency1:CONVersion:MIXer:FFIXed {lo_frequency}")  # LO frequency
        self._write("FREQuency:CONVersion:MIXer:LOMultiplier 3, 2")
        self._write("SOURce1:FREQuency1:CONVersion:MIXer:PFIXed -5")  # LO power
        self._write(f"SOURce1:POWer {if_power}")  # IF power
        self._write("SENSe1:FREQuency1:CONVersion MIXer")  # activate mixer

    def mixer_frequency_sweep_setup(
        self,
        lo_frequency_start: float = 19.6e9,
        steps: int = 7,
        lo_frequency_end: float = 21.6e9,
        if_frequency: float = 2.94912e9,
        lo_power: float = -10,
        if_power: float = -30,
        lo_multiplier: float = 3,
        lo_divider: float = 2,
        conversion: str = "DCLower",
    ) -> None:
        """Sets up mixer for frequency sweep.

        :param lo_frequency_start: Starting frequency (Hz) for LO
        :param steps: Number of steps to take in sweep.
        :param lo_frequency_stop: Stopping frequency (Hz) for LO
        :param if_frequency: Frequency for IF
        :param lo_power: Power (Watts?) for LO
        :param if_power: Power (Watts?) for IF
        :param lo_multiplier: Multiplier for LO
        :param lo_divider: Multiplier for IF
        :param conversion: Defaults to DCLower.
        """
        self._write("SENSe1:SWEEp:TYPE LINear")
        self._write(f"SENSe1:SWEEp:POINts {steps}")
        self._write(f"SENSe1:FREQuency1:STARt {lo_frequency_start}")  # start : 500 MHz')
        self._write(f"SENSe1:FREQuency1:STOP {lo_frequency_end}")  # stop : 2.5 GHz

        self._write("FREQuency:CONVersion:MIXer:IFPort 1")
        self._write("FREQuency:CONVersion:MIXer:RFPort 2")

        self._write("SENSe1:FREQuency1:CONVersion:MIXer:FUND LO")

        self._write("SENSe1:FREQuency1:CONVersion:MIXer:Fixed IF")
        self._write("SENSe1:FREQuency1:CONVersion:MIXer:LOINternal 3")  # LO port 3
        self._write(f"SENSe1:FREQuency1:CONVersion:MIXer:TFRequency {conversion}")  # RF + LO

        self._write(":SENSe1:PHASe:MODE COHerent")
        self._write(":SENSe1:FREQuency1:CONVersion MIXer")

        self._write(f"SENSe1:FREQuency1:CONVersion:MIXer:FFIXed {if_frequency}")  # LO frequency
        self._write(f"FREQuency:CONVersion:MIXer:LOMultiplier {lo_multiplier}, {lo_divider}")
        self._write(f"SOURce1:POWer {if_power}")  # IF power
        self._write(f"SOURce1:FREQuency1:CONVersion:MIXer:PFIXed {lo_power}")  # LO power

        # added to receive in both ports 2 and 4
        self._write(f"SENS1:FREQ4:CONV:ARB {lo_multiplier}, {lo_divider},{if_frequency},SWE")
        self._write("SENSe1:FREQuency4:CONVersion:AWR OFF")
        self._write(f"SENS1:FREQ2:CONV:ARB {lo_multiplier}, {lo_divider},{if_frequency},SWE")
        self._write("SENSe1:FREQuency2:CONVersion:AWR OFF")
        self._write("SOUR:POW2:STAT OFF")
        self._write("SOUR:POW4:STAT OFF")

    def mixer_power_sweep_setup(
        self,
        lo_frequency: float = 20.6e9,
        if_frequency: float = 2.94912e9,
        if_power_start: float = -25,
    ) -> None:
        """Sets up mixer for power sweep.

        :param lo_frequency: Frequency for LO.
        :param if_frequency: Frequency for IF.
        :param if_power_start: Starting power (Watts?) for IF.
        """
        self._write("SENSe1:SWEEp:TYPE POwer")
        self._write("SENSe1:SWEEp:POINts 201")
        self._write(f"SENSe1:FREQuency1:STARt {if_frequency}")  # start : 500 MHz')
        self._write(f"SENSe1:FREQuency1:STOP {if_frequency}")  # stop : 2.5 GHz
        self._write("SOURce1:POWer1 0")  # Base power
        self._write("FREQuency:CONVersion:MIXer:IFPort 1")
        self._write("FREQuency:CONVersion:MIXer:RFPort 2")
        self._write("SENSe1:FREQuency1:CONVersion:MIXer:FIXed LO")
        self._write("SENSe1:FREQuency1:CONVersion:MIXer:FUND IF")
        self._write("SENSe1:FREQuency1:CONVersion:MIXer:LOINternal 3")  # LO port 3
        self._write("SENSe1:FREQuency1:CONVersion:MIXer:TFRequency DCLower")  # RF + LO

        self._write(f"SENSe1:FREQuency1:CONVersion:MIXer:FFIXed {lo_frequency}")  # LO frequency
        self._write("FREQuency:CONVersion:MIXer:LOMultiplier 3, 2")
        self._write("SOURce1:FREQuency1:CONVersion:MIXer:PFIXed -5")  # LO power
        self._write(f"SOURce1:POWer:START {if_power_start}")  # IF power
        self._write("SENSe1:FREQuency1:CONVersion MIXer")  # activate mixer

        self._write("SOURce1:LOTRack")  # LO Track when external LO

    def horn_frequency_sweep_setup(
        self,
        frequency_start: float = 26.5e9,
        frequency_end: float = 29.5e9,
        frequency_step: float = 50e6,
        power: float = -10,
    ) -> None:
        """Setup frequency sweep for horn.

        :param frequency_start: Starting frequency in sweep.
        :param frequency_end: Ending frequency in sweep.
        :param frequency_step: Stepsize (in Hz) for sweep.
        :param power: Power level of horn.
        """
        points: int = int((frequency_end - frequency_start) / (frequency_step + 1))
        self._write(f"SENSe1:SWEEp:POINts {points}")
        self._write(f"SENSe1:FREQuency1:STARt {frequency_start}")
        self._write(f"SENSe1:FREQuency1:STOP {frequency_end}")
        self._write(f"SOURce1:POWer1 {power}")

    def measure_compression_point(self) -> None:
        """Measures compression point."""
        self._write(":SENSe:FREQuency:COMPression:SRCPort 1; RECeiver 2")
        self._write(":SENSe:FREQuency:COMPression:POWer:STARt -20; STOP -10")
        self._write(":SENSe:FREQuency:COMPression:POINt 1.5")

        self._write(":CALCulate:PARameter:MEASure 'Trc1', 'CmpPtPout'")
        self._write(":CALCulate:PARameter:SDEFine 'Trc2', 'CmpPtPin'")

    def absolute_power(self) -> None:
        """Writes absolute power."""
        self._write("CALCulate1:PARameter:SDEFine 'Trc1','b2'")  # a1 if power b2 received power

    def trace_setup(self, trace: str = "'Trc1'", trace_format: str = "'b1'") -> None:
        """Trace setup.

        :param trace: 'Trc1'
        :param trace_format: 'b1'
        """
        self._write(
            f"CALCulate1:PARameter:SDEFine {trace},{trace_format}"
        )  # a1 if power b2 received power

    def set_format(self, display_format: str = "PHase") -> None:
        """Sets format for ZNA.

        :param display_format: Display format for ZNA.
        """
        self._write(f"Calculate1:Format {display_format}")

    def enable_display(self, trace: str = "Trc1") -> None:
        """Enables display.

        :param trace: Trace.
        """
        self._write(":DISPlay:WINDow:STATE ON")
        self._write(f":DISPlay:WINDow:TRACE:FEED {trace}")

    def create_traces(self, lo_frequency: float = 20.6e9) -> None:
        """Create traces.

        :param lo_frequency: LO frequency (Hz)
        """
        # ch1 : Trc1 (=s21), rename Trace
        self._write("CONFigure:CHANnel1:TRACe:REName 'Conv'")
        # Ch1 : Tr2 und Trc3 (Trc1 still defined)
        self._write("CALCulate1:PARameter:SDEFine 'RF_Refl','S11'")
        self._write("DISPlay:WINDow1:TRACe2:FEED 'RF_Refl'")
        self._write("CALCulate1:PARameter:SDEFine 'IF_Refl','S22'")
        self._write("DISPlay:WINDow1:TRACe3:FEED 'IF_Refl'")
        # Ch2 : Trc4 # noqa
        self._write("CONFigure:CHANnel2 ON")  # channel 2
        self._write("CALCulate2:PARameter:SDEFine 'RF_Isol','S21'")
        self._write("DISPlay:WINDow1:TRACe4:FEED 'RF_Isol'")
        # Ch3 : Trc5, 6
        self._write("CONFigure:CHANnel3 ON")  # channel 3
        self._write("CALCulate3:PARameter:SDEFine 'LO_Leak','S13'")
        self._write("DISPlay:WINDow1:TRACe5:FEED 'LO_Leak'")
        self._write("CALCulate3:PARameter:SDEFine 'LO_Thru','S23'")
        self._write("DISPlay:WINDow1:TRACe6:FEED 'LO_Thru'")
        # channel names
        self._write("CONFigure:CHANnel1:NAME 'Ch_M'")
        self._write("CONFigure:CHANnel2:NAME 'CH_RF'")
        self._write("CONFigure:CHANnel3:NAME 'CH_LO'")
        # Adjust channels for measurement
        # channel 1 (arbitrary) remains unchanged
        # channel 2 (base frequency), reset arbitrary mode
        self._write("SENSe2:FREQuency1:CONVersion FUNDamental")
        # trace RF_Isol in channel Ch_RF is measured with active LO!
        self._write("SOURce2:FREQuency3:CONVersion:ARBitrary:IFRequency 1, 1, 3 GHz, FIXed")
        self._write("SOURce2:POWer3:PERManent:STATe ON")
        # channel 3 (LO freqeuncy), reset arbitrary and set LO-frequencies
        self._write("SENSe3:FREQuency1:CONVersion FUNDamental")
        # LO-fix : Start=Stop, sweep-points = 1
        self._write("SENSe3:SWEep:POINts 1")
        self._write(f"SENSe3:FREQuency1:STARt {lo_frequency}")
        self._write(f"SENSe3:FREQuency1:STOP {lo_frequency}")

    @retry_on_failure
    def read_sweep(self) -> str:
        """Read value of sweep.

        :return: Sweep data.
        """
        self._write(":INITIATE:CONTinuous:ALL OFF")
        self._write(":INITIATE:IMMEDIATE:ALL; *WAI")
        return self._query(":CALCULATE1:DATA? SDATA")

    @retry_on_failure
    def setup_averages(self, count: int) -> None:
        """Sets up averages.

        :param count: Count of steps?
        """
        self._write(f":SENS1:AVER:COUN {count}; :AVER ON")

    @retry_on_failure
    def setup_if_bandwidth(self, if_bandwidth: float = 10e3) -> None:
        """Sets up IF Bandwidth.

        :param if_bandwidth: Width of IF band.
        """
        self._write(f":SENS1:BANDwidth:Resolution {if_bandwidth}")

    @retry_on_failure
    def read_magnitude_sweep(self) -> str:
        """Reads magnitude of sweep.

        :return: Magnitude of sweep as string.
        """
        self._write(":INITIATE:CONTinuous:ALL OFF")
        self._write(":SENS1:AVER:Clear")
        self._write(":INITIATE:IMMEDIATE:ALL; *WAI")
        return self._query(":CALCULATE1:DATA? FDATA")

    @retry_on_failure
    def read_magnitude_sweep_multi_trace(self, trace: str = "Trc1") -> str:
        """Reads magnitude of sweep with multi trace.

        :param trace: Trace
        :return: Magnitude of sweep as string.
        """
        self._write("INIT1:IMM")
        self._write("ABOR;*WAI")
        self._write(f"CALC1:PAR:SEL {trace}")
        return self._query(":CALCULATE1:DATA? FDATA")

    @retry_on_failure
    def read_sweep2(self) -> str:
        """Read value of Sweep: 2 Electric Boogaloo.

        :return: Sweep data as string.
        """
        return self._query(":CALCULATE1:DATA? FDATA")

    @retry_on_failure
    def read_sweep_parse(self, trace: str = "Trc1") -> list:
        """Read sweep and parse into list.

        :return: Sweep data as list.
        """
        data_raw = self.read_magnitude_sweep_multi_trace(trace)
        data_split = data_raw.split(",")
        data = []
        for i in range(len(data_split)):
            data.append(float(data_split[i]))
        return data

    @retry_on_failure
    def read_sweep_db(self, channel: int) -> str:
        """Read value of Sweep in db?.

        :param channel: Channel to read from.
        :return: Sweep data as string.
        """
        return self._query(f":CALCULATE{channel}:DATA? FDATA")

    def kfam_freq_sweep(
        self,
        polarization: str = "Theta",
        magnitude_only: bool = True,
        single: bool = False,
    ) -> Union[
        Tuple[floating[Any], floating[Any]],
        Tuple[List[float], List[float]],
        floating[Any],
        List[float],
    ]:
        """KFAM Frequency Sweep."""
        if polarization == "Theta":
            self.set_format(display_format="MAGN")
            data_raw_magnitude: str = self.read_magnitude_sweep_multi_trace(trace="PolTheta")
            if not magnitude_only:
                self.set_format(display_format="PHAS")
                data_raw_phase: str = self.read_magnitude_sweep_multi_trace(trace="PolTheta")
        else:
            self.set_format(display_format="MAGN")
            data_raw_magnitude = self.read_magnitude_sweep_multi_trace(trace="PolPhi")
            if not magnitude_only:
                self.set_format(display_format="PHAS")
                data_raw_phase = self.read_magnitude_sweep_multi_trace(trace="PolPhi")

        data_magnitude_split: List[str] = data_raw_magnitude.split(",")

        data_magnitude: List[float] = []
        for i in range(len(data_magnitude_split)):
            data_magnitude.append(float(data_magnitude_split[i]))

        if not magnitude_only:
            data_phase_split: List[str] = data_raw_phase.split(",")
            data_phase: List[float] = []
            for i in range(len(data_phase_split)):
                data_phase.append(float(data_phase_split[i]))
            if single:
                return np.mean(data_magnitude), np.mean(data_phase)
            else:
                return data_magnitude, data_phase
        else:
            if single:
                return np.mean(data_magnitude)
            else:
                return data_magnitude

    def read_trace_raw(self, trace: str, ch: str = "1") -> list:
        """Read non-sweep trace (read raw real & imag data).

        Args:
            trace (str): name of trace.
            format (str, optional): Data format (PHASe or MAGN). Defaults to 'MAGN'.
            ch (str, optional): ZNA channel. Defaults to '1'.

        Returns:
            list: real and imaginary.
        """
        self._write("CALC{}:PAR:SEL {}".format(ch, trace))
        data = self._query(f"CALC{ch}:DATA? SDAT")
        data_split: list = self.split_data(data)
        return data_split

    def split_data(self, data: str) -> list:
        """Helper function to split data.

        Args:
            data (str): raw data read.

        Returns:
            list: split data.
        """
        data_split = data.split(",")
        new_data = [float(i) for i in data_split]
        return new_data

    def mag_from_real_imag(self, real: float, imag: float, d_z_0: float = -12.8802) -> float:
        """Helper function to convert real and imaginary data to magnitude.

        Args:
            real (float): real part.
            imag (float): imaginary part.
            d_z_0 (float, optional): Constant. Defaults to -12.8802.

        Returns:
            float: magnitude.
        """
        mag = 20 * math.log10(
            math.sqrt(real**2 + imag**2)
        )  # - d_z_0  # TODO only need constant for absolute power
        return mag

    def phase_from_real_imag(self, real: float, imag: float) -> float:
        """Helper function to convert real and imaginary data to phase.

        Args:
            real (float): real part.
            imag (float): imaginary part.

        Returns:
            float: phase.
        """
        phase = math.atan2(imag, real) * (180 / math.pi)
        return phase

    def real_imag_to_magn_phas(self, real: float, imag: float) -> tuple:
        """Helper function to convert real and imaginary to magnitude and phase.

        Args:
            real (float): real part.
            imag (float): imaginary part.

        Returns:
            tuple: magnitude & phase
        """
        return self.mag_from_real_imag(real, imag), self.phase_from_real_imag(real, imag)

    def read_raw_and_format(self, trace: str, ch: str = "1") -> tuple:
        """Read and return raw and formatted data.

        Args:
            trace (str): name of trace.
            ch (str, optional): ZNA channel. Defaults to '1'.

        Returns:
            tuple: real, imag, magnitude, phase.
        """
        raw_data = self.read_trace_raw(trace, ch)
        real = raw_data[0]
        imag = raw_data[1]
        magnitude, phase = self.real_imag_to_magn_phas(real, imag)
        return real, imag, magnitude, phase

    def read_non_continuous_sweep(self, trace: str, points_expected: int) -> tuple:
        """Read non continuous sweep.

        Args:
            trace: name of trace
            points_expected: expected sweep points

        Returns:
            tuple of arrays
        """
        self._write(f"CALC1:PAR:SEL '{trace}'")

        data = self._query("CALC1:DATA:NSW:FIRS? SDAT,1,{}".format(points_expected))
        data_split = self.split_data(data)
        real_ = []
        imag_ = []
        magn_ = []
        phase_ = []
        for i in range(int(len(data_split) / 2)):
            real = data_split[2 * i]
            imag = data_split[2 * i + 1]
            magnitude, phase = self.real_imag_to_magn_phas(real, imag)
            real_.append(real)
            imag_.append(imag)
            magn_.append(magnitude)
            phase_.append(phase)
        return real_, imag_, magn_, phase_

    def set_non_continous_sweep(self, points_expected: int) -> None:
        """Set ZNA to non continous sweep.

        Args:
            points_expected: number of points to expect in sweep
        """
        self._write("SWE:COUN {}".format(points_expected + 10))
        self._write("TRIG:SOUR EXT")
        self._write("TRIG:EINP EXTA")
        self._write("TRIG:SLOP POS")
        self._write("TRIG:LINK 'SWE'")
        self._write("INIT:SCOP SING")
        self._write("INIT:CONT OFF")
        self._write("INIT:IMM")

    def set_continous_sweep(self) -> None:
        """Set ZNA to continuous sweep."""
        self._write("INIT:CONT ON")
        self._write("TRIG:SOUR IMM")

    def get_non_sweep_count(self) -> int:
        """Get non sweep points count.

        Returns:
            number of points in sweep count
        """
        return int(self._query("CALC1:DATA:NSW:COUN?"))
