"""Driver for CMP200."""

import json
import os
from typing import Optional

import instrument_lib
from instrument_lib.utils.gpib_number import GPIBNumber
from instrument_lib.instruments.instrument import SCPIInstrument


class RS_CMP200(SCPIInstrument):
    """CMP 200.

    This instrument is an IF tester that combines vector signal analyzer
    and ARB based generator functionality.
    """

    ACCEPTED_MODELS = [
        "CMP200",
    ]

    def __init__(
        self,
        gpib: GPIBNumber | None = None,
        ip_address: str | None = None,
        usb: tuple[str, str, str] | None = None,
        wireless: bool = False,
        simulate: bool = False,
    ):
        """Constructor.

        :param gpib: GPIB Number, defaults to None
        :param ip_address: IP Address as a string, defaults to None
        :param wireless: If connection is wireless, defaults to False
        """
        super().__init__(gpib, ip_address, usb, wireless, simulate)
        self.rsinstrument: bool = True

    def generator_on(self) -> None:
        """Turns on generator."""
        self._write("SOUR:GPRF:GEN:STAT ON")

    def generator_off(self) -> None:
        """Turns off generator."""
        self._write("SOUR:GPRF:GEN:STAT OFF")

    def init_device(self) -> None:
        """Used to reset the CMP200 to default settings."""
        self._write("*RST")
        self._write("*CLS")

    def init_ports_and_routes(
        self,
        freq_range_low: float = 26.0e9,
        freq_range_high: float = 30.0e9,
        tx_attenuation: float = 0.0,
        rx_attenuation: float = 2.7,
        tx_port: int = 2,
        rx_port: int = 3,
    ) -> None:
        """Initialization for ports and routes.

        :param freq_range_low: Freq range low value, defaults to 26.0e9.
        :param freq_range_high: Freq range high value, defaults to 30.0e9.
        :param tx_attenuation: attenuation for tx, defaults to 0.0.
        :param rx_attenuation: attenuation for rx, defaults to 2.7.
        :param tx_port: tx_port, defaults to 2.
        :param rx_port: rx_port, defaults to 3.
        """
        self._write(
            f"CRE:SYST:ATT:CTAB 'GEN_FDC_RRH2_RF1', {freq_range_low}, {tx_attenuation}, {freq_range_high}, {tx_attenuation}"
        )
        self._write(
            f"CRE:SYST:ATT:CTAB 'ANA_FDC_RRH1_RF1', {freq_range_low}, {rx_attenuation}, {freq_range_high}, {rx_attenuation}"
        )
        self._write(f"CONF:TENV:SPAT:CTAB:TX 'Port{tx_port}.RRH.RF1', 'GEN_FDC_RRH2_RF1'")
        self._write(f"CONF:TENV:SPAT:CTAB:RX 'Port{rx_port}.RRH.RF1', 'ANA_FDC_RRH1_RF1'")
        self._write(f"ROUT:GPRF:MEAS:SPAT 'Port{rx_port}.RRH.RF1'")
        self._write(f"ROUT:NRMM:MEAS:SPAT 'Port{rx_port}.RRH.RF1'")
        self._write(f"ROUT:GPRF:GEN:SPAT 'Port{tx_port}.RRH.RF1'")

    def select_arb_file(
        self,
        file_name: str = "@WAVEFORM//NR5G_FR2_All_UL_Slots_100MHz_SCS120_CP_OFDM_RB0_66_64QAM.wv",
    ) -> None:
        """ARB file to pass into generator.

        :param file_name: ARB , defaults to "@WAVEFORM//NR5G_FR2_All_UL_Slots_100MHz_SCS120_CP_OFDM_RB0_66_64QAM.wv"
        """
        self._write(f"SOUR:GPRF:GEN:ARB:FILE '{file_name}'")

    def set_carrier_freq(self, freq_mhz: int = 28000) -> None:
        """Set frequency of unmodulated RF carrier.

        :param freq_mhz: Frequency in MHz, defaults to 28000
        """
        self._write(f"SOUR:GPRF:GEN:RFS:FREQ {freq_mhz} MHZ")

    def set_gen_baseband_mode(self, bb_mode: str = "ARB") -> None:
        """Set GPRF baseband mode.

        :param bb_mode: Baseband mode, defaults to "ARB".
        """
        self._write(f"SOUR:GPRF:GEN:BBM {bb_mode}")

    def select_rf_analyzer_freq(self, freq_mhz: int = 28000) -> None:
        """Set the center frequency of the RF analyzer.

        :param freq_mhz: Frequency in MHz, defaults to 28000
        """
        self._write(f"CONF:GPRF:MEAS:RFS:FREQ {freq_mhz} MHZ")

    def select_cc_1_carrier_freq(self, freq_mhz: int = 28000) -> None:
        """Selects the center frequency of carrier CC1.

        :param freq_mhz: Frequency in MHz, defaults to 28000
        """
        self._write(f"CONF:NRMM:MEAS:RFS:FREQ {freq_mhz} MHZ")

    def set_carrier_enp(self, enp: float = 0.00) -> None:
        """Sets expected nominal power of measured signal.

        :param enp: Expected Nominal Power, defaults to 0.00.
        """
        self._write(f"CONF:NRMM:MEAS:RFS:ENP {enp}")

    def set_ul_dl_pattern(self, ul_dl_pattern: str = "TDD") -> None:
        """Sets ul_dl pattern for carrier.

        :param ul_dl_pattern: Pattern format you are using for carrier, defaults to "TDD"
        """
        self._write(f"CONF:NRMM:MEAS:MEV:DMOD {ul_dl_pattern}")

    def set_ul_dl_pattern_60kHz(
        self,
        num_dl_slots: int = 0,
        num_dl_symbols: int = 0,
        num_ul_slots: int = 4,
        num_ul_symbols: int = 0,
    ) -> None:
        """Configures the UL-DL pattern for 60KHz.

        :param num_dl_slots: Number of Downlink slots, defaults to 0.
        :param num_dl_symbols: Number of Downlink symbols, defaults to 0.
        :param num_ul_slots: Number of Uplink slots, defaults to 4.
        :param num_ul_symbols: Number of Uplink symbols, defaults to 0.
        """
        self._write(
            f"CONF:NRMM:MEAS:ULDL:PATT S60K,{num_dl_slots},{num_dl_symbols},{num_ul_slots},{num_ul_symbols}"
        )

    def set_ul_dl_pattern_120kHz(
        self,
        num_dl_slots: int = 0,
        num_dl_symbols: int = 0,
        num_ul_slots: int = 8,
        num_ul_symbols: int = 0,
    ) -> None:
        """Configures the UL-DL pattern for 120KHz.

        :param num_dl_slots: Number of Downlink slots, defaults to 0.
        :param num_dl_symbols: Number of Downlink symbols, defaults to 0.
        :param num_ul_slots: Number of Uplink slots, defaults to 8.
        :param num_ul_symbols: Number of Uplink symbols, defaults to 0.
        """
        self._write(
            f"CONF:NRMM:MEAS:ULDL:PATT S120K,{num_dl_slots},{num_dl_symbols},{num_ul_slots},{num_ul_symbols}"
        )

    def set_ul_dl_periodicity(self, periodicity: str = "MS1") -> None:
        """Configures the periodicity of the UL-DL pattern.

        :param periodicity: Periodicity that you are setting, defaults to "MS1".
        """
        self._write(f"CONF:NRMM:MEAS:ULDL:PER {periodicity}")

    def select_measurement_subcarrier_spacing(self, spacing: str = "S120K") -> None:
        """Selects the subcarrier spacing for the meeasurement, for all carriers.

        :param spacing: subcarrier spacing, defaults to "S120K".
        """
        self._write(f"CONF:NRMM:MEAS:CCAL:TXBW:SCSP {spacing}")

    def set_carrier_physical_cell_id(self, plc: int = 0) -> None:
        """Specifies the physical cell ID of carrier.

        :param plc: physical cell id, defaults to 0.
        """
        self._write(f"CONF:NRMM:MEAS:CC1:PLC {plc}")

    def set_carrier_dmrs_type_a_position(self, tap: int = 2) -> None:
        """Specifies the dmrs-TypeA-Postiion of carrier.

        :param tap: DMRS type a position, defaults to 2.
        """
        self._write(f"CONF:NRMM:MEAS:CC1:TAP {tap}")

    def set_carrier_channel_bandwidth(self, bandwidth: str = "B100") -> None:
        """Specifies channel bandwidth of carrier.

        :param bandwidth: Set channel bandwidth, defaults to "B100".
        """
        self._write(f"CONF:NRMM:MEAS:CC1:CBAN {bandwidth}")

    def set_carrier_bwp_settings(
        self,
        bwp: int = 0,
        subcarrier_spacing: str = "S120K",
        cyclic_prefix: str = "NORM",
        num_rbs: int = 66,
        start_rb: int = 0,
    ) -> None:
        """Configures basic BWP properties of carrier.

        :param bwp: The BWP you are updating settings for.
        :param subcarrier_spacing: Subcarrier spacing, defaults to "S120K".
        :param cyclic_prefix: Cyclic prefix, defaults to "NORM".
        :param num_rbs: Number of RBs, defaults to 66.
        :param start_rb: Start RB, defaults to 0.
        """
        self._write(
            f"CONF:NRMM:MEAS:CC1:BWP BWP{bwp},{subcarrier_spacing},{cyclic_prefix},{num_rbs},{start_rb}"
        )

    def set_carrier_pusch_allocation(
        self,
        mapping_type: str = "A",
        num_sym: int = 14,
        start_sym: int = 0,
        num_rbs: int = 66,
        start_rb: int = 0,
        mod_scheme: str = "Q64",
    ) -> None:
        """Specifies settings related to PUSCH allocation for carrier.

        :param mapping_type: Channel mapping type, defaults to "A".
        :param num_sym: Number of allocated OFDM symbols in each uplink slot, defaults to 14.
        :param start_sym: Index of the first allocated OFDM symbol in each uplink slot, defaults to 0.
        :param num_rbs: Number of allocated uplink RBs, defaults to 66.
        :param start_rb: Index of the first allocated RB, defaults to 0.
        :param mod_scheme: Modulation scheme, defaults to "Q64".
        """
        self._write(
            f"CONF:NRMM:MEAS:CC1:ALL:PUSC {mapping_type},{num_sym},{start_sym},{num_rbs},{start_rb},{mod_scheme}"
        )

    def set_carrier_pusch_additional_allocation(
        self,
        dmrs_length: int = 1,
        cdm_groups_no_data: int = 1,
        dmrs_relative_power: float = 0.0,
        antenna_port: int = 0,
    ) -> None:
        """Configures special PUSCH settings for carrier.

        :param dmrs_length: Length of DM-RS in symbols, defaults to 1.
        :param cdm_groups_no_data: CDM Groups w/o data, defaults to 1.
        :param dmrs_relative_power: Power of DM-RS relative to PUSCH power, defaults to 0.0.
        :param antenna_port: Antenna Port, defaults to 0.
        """
        self._write(
            f"CONF:NRMM:MEAS:CC1:ALL:PUSC:ADD {dmrs_length},{cdm_groups_no_data},{dmrs_relative_power},{antenna_port}"
        )

    def set_carrier_bwp_transform_precoding(
        self, bwp: int = 0, transform_precoding: str = "OFF"
    ) -> None:
        """Specifies whether carrier uses a transform precoding function.

        :param bwp: BWP you are setting transform_precoding state on, defaults to 0.
        :param transform_precoding: transform_precoding state, defaults to "OFF".
        """
        self._write(f"CONF:NRMM:MEAS:CC1:BWP:PUSC:DFTP BWP{bwp},{transform_precoding}")

    def set_carrier_bwp_dmrs_mapping(
        self,
        bwp: int = 0,
        configuration_type: int = 1,
        additional_position: int = 2,
        max_length: int = 1,
    ) -> None:
        """Configures the DM-RS for mapping type A.

        :param bwp: BWP you are updating settings for, defaults to 0.
        :param configuration_type: DM-RS setting "dmrs-Type", defaults to 1.
        :param additional_position: DM-RS setting "dmrs-AdditionalPosition", defaults to 2.
        :param max_length: DM-RS setting "maxLength", defaults to 1.
        """
        self._write(
            f"CONF:NRMM:MEAS:CC1:BWP:PUSC:DMTA BWP{bwp},{configuration_type},{additional_position},{max_length}"
        )

    def set_gen_rms_level(self, level: float = -30.00) -> None:
        """Sets the base RMS level of the RF generator.

        :param level: Level measured in dBm, defaults to -30.00.
        """
        self._write(f"SOUR:GPRF:GEN:RFS:LEV {level}")

    def set_user_margin(self, umar: float = 12.0) -> None:
        """Sets the margin that the measurement adds to the expected nominal power to determine the reference power.

        :param umar: User margin, defaults to 12.0.
        """
        self._write(f"CONF:NRMM:MEAS:RFS:UMAR {umar}")

    def set_measurement_statistic_counts(
        self, power: int = 10, mod: int = 10, semask: int = 1, aclr: int = 1
    ) -> None:
        """Sets statistic counts for measurements.

        :param power: Power, defaults to 10.
        :param mod: Modulation, defaults to 10.
        :param semask: Spectrum Emissions Mask, defaults to 1.
        :param aclr: , defaults to 1.
        """
        self._write(f"CONF:NRMM:MEAS:MEV:SCO:POW {power};MOD {mod};SPEC:SEM {semask};ACLR {aclr}")

    def set_trigger_source(self, trigger_source: str = "Free Run (Fast Sync)") -> None:
        """Selects the source of the trigger events.

        :param trigger_source: Source of trigger events, defaults to "Free Run (Fast Sync)".
        """
        self._write(f"TRIG:NRMM:MEAS:MEV:SOUR '{trigger_source}'")

    def start_measurement(self) -> None:
        """Starts measurement sequence."""
        self._write("ABOR:NRMM:MEAS:MEV")
        self._write("INIT:NRMM:MEAS:MEV")

    def enable_measurements(self) -> None:
        """SCPI commands that still dont have a function."""
        self._write("CONF:NRMM:MEAS:MEV:RES:ALL ON,OFF,OFF,ON,OFF,ON,OFF,ON,ON,OFF,OFF,OFF")

    def get_results(self) -> dict[str, str]:
        """Gets readings from current settings."""
        results: str = self._query("FETC:NRMM:MEAS:MEV:MOD:AVER?")
        results_dict: dict[str, str] = self.parse_results(results)

        print(f"Power RMS: {results_dict['power_rms']}")
        print(f"Power Peak: {results_dict['power_peak']}")
        print(f"EVM RMS: {results_dict['evm']}")
        print(f"EVM Peak: {results_dict['evm_peak']}")
        print(f"EVM_DMRS: {results_dict['evm_dmrs']}")

        return results_dict

    def parse_results(self, result_str: str) -> dict[str, str]:
        """Parses results from CMP200 and returns them in a dictionary format.

        :param result_str: Data read from CMP200 in str format.
        :return: Dict containing measurement data.
        """
        result_list: list[str] = result_str.split(",")
        result_dict: dict[str, str] = {}

        evm_low: float = float(result_list[2])
        evm_high: float = float(result_list[3])
        evm: str = str(max(evm_low, evm_high))
        result_dict["evm"] = evm

        evm_peak_low: float = float(result_list[4])
        evm_peak_high: float = float(result_list[5])
        evm_peak: str = str(max(evm_peak_high, evm_peak_low))
        result_dict["evm_peak"] = evm_peak

        evm_dmrs_low: float = float(result_list[21])
        evm_dmrs_high: float = float(result_list[22])
        evm_dmrs: str = str(max(evm_dmrs_low, evm_dmrs_high))
        result_dict["evm_dmrs"] = evm_dmrs

        result_dict["power_rms"] = result_list[18]

        result_dict["power_peak"] = result_list[19]

        return result_dict
