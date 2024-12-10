"""PNAX module."""

from time import sleep
from typing import List, Optional, cast

from instrument_lib.utils import GPIBNumber
from instrument_lib.instruments.instrument import SCPIInstrument


class KS_PNA(SCPIInstrument):
    """Class for the Keysight self."""

    ACCEPTED_MODELS = [
        "N5247B",
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

        :param gpib: GPIB number.
        :param wireless: wireless.
        """
        self.rsinstrument = False
        super().__init__(gpib, ip_address, usb, wireless, simulate)

    def reset(self) -> None:
        """Reset the voltage of the power supply."""
        self._write("*RST")

    def clear_errors(self) -> None:
        """Clear errors."""
        self._write("*CLS")

    def averaging_off(self, channel: int = 1) -> None:
        """_summary_.

        :param channel: _description_, defaults to 1
        """
        self._write(f"SENS{channel}:AVER OFF")

    def avergaging_on(self, channel: int = 1) -> None:
        """_summary_.

        :param channel: _description_, defaults to 1
        """
        self._write(f"SENS{channel}:AVER ON")

    def create_trace(
        self, trace: str = "S1,1", trnum: int = 1, channel: int = 1, window: int = 1
    ) -> None:
        """_summary_.

        :param trace: _description_, defaults to "S1,1"
        :param trnum: _description_, defaults to 1
        :param channel: _description_, defaults to 1
        :param window: _description_, defaults to 1
        """
        traces = self.get_trace_list(channel=channel)
        trnum = int(len(traces) / 2 + 1)
        name = trace.replace(",", "")
        param = trace.replace(",", "_")
        self._write(f"CALC{channel}:PAR:EXT 'CH{channel}_{name}_{trnum}', '{param}'")

        self._write(f"DISP:WIND{window}:STAT ON")

        self._write(f"DISP:WIND{window}:TRAC{trnum}:FEED'CH{channel}_{name}_{trnum}'")

    def delete_all_measurements(self) -> None:
        """_summary_."""
        self._write("CALC:PAR:DEL:ALL")

    def delete_measurement_by_name(self, name: str = "") -> None:
        """_summary_."""
        self._write(f"CALC:PAR:DEL '{name}'")

    def disable_scale_coupling(self) -> None:
        """_summary_."""
        self._write("DISP:WIND:TRAC:Y:COUP OFF")

    def enable_scale_coupling(self) -> None:
        """_summary_."""
        self._write("DISP:WIND:TRAC:Y:COUP ON")

    def fpreset(self) -> None:
        """_summary_."""
        # Preset the PNA and wait for preset completion via use of *OPC?
        # *OPC? holds-off subsequent commands and places a "1" on the output buffer
        # when the predicating command functionality is complete. Do not use a loop
        # with *OPC? as there is no change from a 0 condition to a 1 condition.
        # A '1' is placed on the output buffer when the operation is complete.
        self._write("SYST:FPR; *OPC?")
        self._read()

    def create_ratioed_measurement(
        self,
        name: str = "CH1_BR1",
        ratio: str = "BR1",
        trace: int = 1,
        window: int = 1,
        src_port: int = 1,
    ) -> None:
        """_summary_.

        :param name: _description_, defaults to "CH1_BR1"
        :param ratio: _description_, defaults to "B"
        :param trace: _description_, defaults to 1
        :param window: _description_, defaults to 1
        :param src_port: _description_, defaults to 1
        """
        self._write(f"CALC:PAR:EXT '{name}','{trace}'")
        self._write(f"DISP:WIND{window}:TRAC{trace}:FEED '{name}','{src_port}'")

    def create_nonratioed_measurement(
        self,
        name: str = "CH1_B",
        ratio: str = "B",
        trace: int = 1,
        window: int = 1,
        src_port: int = 1,
    ) -> None:
        """_summary_.

        :param name: _description_, defaults to "CH1_B"
        :param ratio: _description_, defaults to "B"
        :param trace: _description_, defaults to 1
        :param window: _description_, defaults to 1
        :param src_port: _description_, defaults to 1
        """
        self._write(f"CALC:PAR:EXT '{name}', '{trace}'")
        self._write(f"DISP:WIND{window}:TRAC{trace}:FEED '{name}', '{src_port}'")

    def get_bit_order(self) -> str:
        """_summary_.

        :return: _description_
        """
        self._write("FORM:BORD?")
        return self._read()

    def get_next_trace_number(self, wnum: int = 1) -> str:
        """_summary_.

        :param wnum: _description_, defaults to 1
        :return: _description_
        """
        return self._query(f"DISP:WIND{wnum}:TRAC:NEXT?")

    def get_number_of_points(self, channel: int = 1) -> float:
        """_summary_.

        :param channel: _description_, defaults to 1
        """
        return round(float(self._query(f"SENS{channel}:SWE:POIN?")))

    def get_receiver_temp(self) -> float:
        """_summary_."""
        self._write("SENS:TEMP? FAHR; *OPC?")
        return round(float(self._read()), 1)

    def get_start_frequency(self) -> float:
        """_summary_."""
        return float(self._query("SENS:FREQ:STAR?"))

    def get_stop_frequency(self) -> float:
        """_summary_."""
        return float(self._query("SENS:FREQ:STOP?"))

    def get_trace_by_number(self, trnum: int = 1, wnum: int = 1) -> None:
        """_summary_.

        :param trnum: _description_, defaults to 1
        :param wnum: _description_, defaults to 1
        """
        self._write(f"DISP:WIND{wnum}:TRAC{trnum}:SEL")

    def hide_softkeys(self) -> None:
        """_summary_."""
        self._write("DISP:TOOL:ENTR 0")

    def hide_virtual_hardkeys(self) -> None:
        """_summary_."""
        self._write("DISP:TOOL:KEYS 0")

    def noise_source_off(self) -> None:
        """_summary_."""
        self._write("OUTP:MAIN:NOIS OFF")

    def noise_source_on(self) -> None:
        """_summary_."""
        self._write("OUTP:MAIN:NOIS ON")

    def output_off(self) -> None:
        """_summary_."""
        self._write("OUTP OFF")

    def output_on(self) -> None:
        """_summary_."""
        self._write("OUTP ON")

    def save_displayed_traces_csv(self, file: str = "measurement.csv") -> None:
        """_summary_.

        :param file: _description_, defaults to "measurement.csv"
        """
        self._write(f"MMEM:STOR:DATA '{file}','CSV Formetted Data,'displayed','DB',-1")

    def save_gca_data(self, file: str = "measurement.csv") -> None:
        """_summary_.

        :param file: _description_, defaults to "measurement.csv"
        """
        self._write(f"MMEMory:STORe:DATA '{file}','gca sweep data','displayed','displayed',-1")

    def save_screen(self, file: str = "image.bmp") -> None:
        """_summary_.

        :param file: _description_, defaults to "image.bmp"
        """
        self._write(f"MMEM:STOR:SSCR '{file}'")

    def save_state(self, file: str = "state.csa") -> None:
        """_summary_.

        :param file: _description_, defaults to "state.csv"
        """
        self._write(f"MMEM:STOR:CSAR '{file}'")

    def recall_state(self, file: str = "state.csa", recall_timeout: int = 10000) -> None:
        """Tell the instrument to recall the state from the specific file.

        :param file: _description_, defaults to "state.csa"
        :param recall_timeout: Time in milliseconds to wait to recall the state.
        """
        old_pnax_timeout = self.instrument.timeout
        self.instrument.timeout = recall_timeout

        result = 0
        self._write(f"MMEM:LOAD:CSAR '{file}'")
        while not result:
            sleep(1)
            result = int(self._query("*OPC?"))

        self.instrument.timeout = old_pnax_timeout

    def scale_method(self, method: str = "ALL") -> None:
        """_summary_.

        :param method: _description_, defaults to "ALL"
        """
        self._write(f"DISP:WIND:TRAC:Y:COUP:METH {method}")

    def set_all_traces_format(self, frmt: str = "MLOG", channel: int = 1) -> None:
        """_summary_.

        :param frmt: _description_, defaults to "MLOG"
        :param channel: _description_, defaults to 1
        """
        self._write(f"CALC{channel}:FORM {frmt}")

    def set_bit_order_normal(self) -> None:
        """_summary_."""
        self._write("FORM:BORD NORM")

    def set_bit_order_swapped(self) -> None:
        """_summary_."""
        self._write("FORM:BORD SWAP")

    def set_data_format_real32(self) -> None:
        """_summary_."""
        self._write("FORM:DATA REAL,32")

    def set_data_format_real64(self) -> None:
        """_summary_."""
        self._write("FORM:DATA REAL,64")

    def set_dwell_time(self, time: float = 0, channel: int = 1) -> None:
        """_summary_.

        :param time: _description_, defaults to 0
        :param channel: _description_, defaults to 1
        """
        self._write(f"SENS{channel}:SWE:DWEL  {time}")

    def set_gca_linear_input_power_level(self, power: float = -10, channel: int = 1) -> None:
        """_summary_.

        :param power: _description_, defaults to -10
        :param channel: _description_, defaults to 1
        """
        self._write(f"SENS{channel}:GCS:POW:LIN:INP:LEV {power}")

    def set_gca_number_of_frequency_points(self, points: int = 101, channel: int = 1) -> None:
        """_summary_.

        :param points: _description_, defaults to 101
        :param channel: _description_, defaults to 1
        """
        self._write(f"SENS{channel}:GCS:SWE:FREQ:POIN {points}")

    def set_gca_number_of_power_points(self, points: int = 21, channel: int = 1) -> None:
        """_summary_.

        :param points: _description_, defaults to 21
        :param channel: _description_, defaults to 1
        """
        self._write(f"SENS{channel}:GCS:SWE:POW:POIN {points}")

    def set_marker(
        self, freq: float = 26e9, trace: int = 1, marker: int = 1, channel: int = 1
    ) -> None:
        """_summary_.

        :param freq: _description_, defaults to 26e9
        :param trace: _description_, defaults to 1
        :param channel: _description_, defaults to 1
        """
        self._write(f"CALC{channel}:PAR:MNUM {trace}")
        self._write(f"CALC{channel}:MEAS{trace}:MARK{marker}:X {freq}")

    def set_marker_format(
        self, frmt: str = "MLOG", marker: int = 1, trace: int = 1, channel: int = 1
    ) -> None:
        """_summary_.

        :param frmt: _description_, defaults to "MLOG"
        :param marker: _description_, defaults to 1
        :param trace: _description_, defaults to 1
        :param channel: _description_, defaults to 1
        """
        self._write(f"CALC{channel}:PAR:MNUM {trace}")
        self._write(f"CALC{channel}:MEAS:MARK{marker}:FORM {frmt}")

    def set_rec_attenuator(self, port: int = 2, attenutation: float = 10, channel: int = 1) -> None:
        """_summary_.

        :param port: _description_, defaults to 2
        :param attenutation: _description_, defaults to 10
        :param channel: _description_, defaults to 1
        """
        self._write(f"SOUR{channel}:POW{port}:ATT:REC:TEST {attenutation}; *OPC?")
        self._read()

    def set_start_power_level(self, start: float = -33, port: int = 1) -> None:
        """_summary_.

        :param start: _description_, defaults to -33
        :param port: _description_, defaults to 1
        """
        self._write(f"SOUR:POW{port}:STAR {start}")

    def set_stop_power_level(self, end: float, port: int = 1) -> None:
        """_summary_.

        :param end: _description_
        :param port: _description_, defaults to 1
        """
        self._write(f"SOUR:POW{port}:STOP {end}")

    def set_sweep_time(self, time: float = 1) -> None:
        """_summary_.

        :param time: _description_, defaults to 1
        """
        self._write(f"SENS:SWE:TIME {time}")

    def set_wind_trace_state(self, trnum: int = 1, wnum: int = 1, state: str = "ON") -> None:
        """_summary_.

        :param trnum: _description_, defaults to 1
        :param wnum: _description_, defaults to 1
        :param state: _description_, defaults to "ON"
        """
        self._write(f"DISP:WIND{wnum}:TRAC{trnum}:STATE {state}")

    def setup_sparameters(self, channel: int = 1, window: int = 1) -> None:
        """_summary_.

        :param channel: _description_, defaults to 1
        :param window: _description_, defaults to 1
        """
        # Preset the PNA and wait for preset completion via use of *OPC?
        # *OPC? holds-off subsequent commands and places a "1" on the output buffer
        # when the predicating command functionality is complete. Do not use a loop
        # with *OPC? as there is no change from a 0 condition to a 1 condition.
        # A '1' is placed on the output buffer when the operation is complete.
        self._write("SYST:FPRESET; *OPC?")
        self._read()

        # Select the default measurement name as assigned on preset.
        # To catalog the measurement names, by channel number, use the
        # 'CALCulate[n]:PARameter:CATalog?' command where [n] is the channel
        # number. The channel number, n, defaults to "1" and is optional.
        # Measurement name is case sensitive.
        self._write(f"CALC{channel}:PAR:DEL:ALL; *OPC?")
        self._read()
        self._write(f"CALC{channel}:PAR:EXT 'CH{channel}_S11', 'S1_1'")
        self._write(f"CALC{channel}:PAR:EXT 'CH{channel}_S12', 'S1_2'")
        self._write(f"CALC{channel}:PAR:EXT 'CH{channel}_S21', 'S2_1'")
        self._write(f"CALC{channel}:PAR:EXT 'CH{channel}_S22', 'S2_2'")

        # Turn on window 1
        self._write("DISP:WIND" + str(window) + ":STAT ON")

        # Place traces on window 1
        self._write(f"DISP:WIND{window}:TRAC1:FEED 'CH{channel}_S11'")
        self._write(f"DISP:WIND{window}:TRAC2:FEED 'CH{channel}_S12'")
        self._write(f"DISP:WIND{window}:TRAC3:FEED 'CH{channel}_S21'")
        self._write(f"DISP:WIND{window}:TRAC4:FEED 'CH{channel}_S22'")

        self._write("*OPC?")
        self._read()

    def show_softkeys(self) -> None:
        """_summary_."""
        self._write("DISP:TOOL:ENTR 1")

    def show_virtual_hardkeys(self) -> None:
        """_summary_."""
        self._write("DISP:TOOL:KEYS 1")

    def turn_marker_on(self, trace: int = 1, number: int = 1, channel: int = 1) -> None:
        """_summary_.

        :param trace: _description_, defaults to 1
        :param number: _description_, defaults to 1
        :param channel: _description_, defaults to 1
        """
        self._write(f"CALC{channel}:PAR:MNUM {trace}")
        self._write(f"CALC{channel}:MARK {number}")

    def clear_traces(self, channel: int = 1) -> None:
        """_summary_.

        :param channel: _description_, defaults to 1
        """
        self._write(f"CALC{channel}:PAR:DEL:ALL")

    def create_sparam_measurement(
        self,
        name: str = "CH!_S11",
        param: str = "S1_1",
        trace: int = 1,
        window: int = 1,
        load_port: str = "",
    ) -> None:
        """_summary_.

        :param name: _description_, defaults to "CH!_S11"
        :param param: _description_, defaults to "S1_1"
        :param trace: _description_, defaults to 1
        :param window: _description_, defaults to 1
        :param load_port: _description_, defaults to ""
        """
        if load_port != "":
            if param == "S1_1":
                self._write(f"CALC:PAR:EXT '{name}', '{param}'")
                self._write(f"DISP:WIND{window}:TRAC{trace}:FEED '{name}', '{load_port}'")
            elif param == "S2_2":
                self._write(f"CALC:PAR:EXT '{name}', '{param}'")
                self._write(f"DISP:WIND{window}:TRAC{trace}:FEED '{name}', '{load_port}'")
            else:
                self._write(f"CALC:PAR:EXT '{name}', '{param}'")
                self._write(f"DISP:WIND{window}:TRAC{trace}:FEED '{name}'")
        else:
            if param == "S1_1":
                self._write(f"CALC:PAR:EXT '{name}', '{param}'")
                self._write(f"DISP:WIND{window}:TRAC{trace}:FEED '{name}', 2")
            elif param == "S2_2":
                self._write(f"CALC:PAR:EXT '{name}', '{param}'")
                self._write(f"DISP:WIND{window}:TRAC{trace}:FEED '{name}', 1")
            else:
                self._write(f"CALC:PAR:EXT '{name}', '{param}'")
                self._write(f"DISP:WIND{window}:TRAC{trace}:FEED '{name}'")

    def get_trace_list(self, channel: int = 1) -> list[str]:
        """_summary_.

        :param channel: _description_, defaults to 1
        :return: _description_
        """
        traces: str = self._query(f"CALC{channel}:PARameter:CATalog:EXTended?")
        traces = traces.replace('"', "")
        trace_list: list[str] = traces.split(",")
        for i, item in enumerate(trace_list):
            trace_list[i] = item.replace("_", ",")

        return trace_list

    def set_start_frequency(self, start: float = 15e9, channel: int = 1) -> None:
        """_summary_.

        :param start: _description_, defaults to 15e9
        :param channel: _description_, defaults to 1
        """
        self._write(f"SENSE{channel}:FREQ:STAR {start}")

    def set_stop_frequency(self, stop: float = 35e9, channel: int = 1) -> None:
        """_summary_.

        :param stop: _description_, defaults to 35e9
        :param channel: _description_, defaults to 1
        """
        self._write(f"SENS{channel}:FREQ:STOP {stop}")

    def set_number_of_points(self, points: int = 201, channel: int = 1) -> None:
        """_summary_.

        :param points: _description_, defaults to 201
        :param channel: _description_, defaults to 1
        """
        self._write(f"SENS {channel}:SQE:POIN {points}")

    def set_power_level(self, port: int = 1, channel: int = 1, power: float = -10) -> None:
        """_summary_.

        :param port: _description_, defaults to 1
        :param channel: _description_, defaults to 1
        :param power: _description_, defaults to -10
        """
        self._write(f"SOUR{channel}:POW{port} {power}")

    def set_IFBW(self, IFBW: float = 1e3, channel: int = 1) -> str:  # noqa: N802,N803
        """_summary_.

        :param IFBW: _description_, defaults to 1e3
        :param channel: _description_, defaults to 1
        """
        self._write(f"SENS{channel}:BAND{IFBW}; *OPC?")
        opc: str = self._read()
        return opc

    def set_sweep_mode(self, mode: str = "CONT", channel: int = 1) -> None:
        """_summary_.

        :param mode: _description_, defaults to "CONT"
        :param channel: _description_, defaults to 1
        """
        self._write(f"SENS{channel}:SWE:MODE {mode}; *OPC?")
        self._read()

    def read_SNP(self, ports: str = "1,2") -> str:  # noqa: N802
        """Read SNP."""
        self._write("CALC:PAR:MNUM 1")
        # self._write('MMEM:STOR:TRAC:FORM:SNP DB; *OPC?')  # noqa: E800
        # opc = self._read()  # noqa: E800

        # if file != '':  # noqa: E800
        # print('CALC:DATA:SNP:PORTs? ' + str(ports) + '; *OPC?')  # noqa: E800
        self._write('CALC:DATA:SNP:PORTs? "' + str(ports) + '"; *OPC?')
        snp = self._read()
        return snp

    def save_SNP(self, ports: str = "1,2", file: str = "", channel: int = 1) -> None:  # noqa: N802
        """Save SNP."""
        self._write("CALC" + str(channel) + ":PAR:SEL " + "CH" + str(channel) + "_S11_1; *OPC?")
        self._read()
        """
        #print(str(self.get_channel_type(channel = channel)))  # noqa: E800
        #print(str(self._query('SYSTem:CHANnels:CATalog?')))  # noqa: E800
        channel_numbers = str(self._query('SYSTem:CHANnels:CATalog?')).replace('"','').split(',')
        for i in range(len(channel_numbers)):
            print(str(channel_numbers[i]))
        #print('Active measurement class: '
        # + str(self._query('SYSTem:ACTive:MCLass?').replace(' ','').split('"')[1]))
        """
        self._write("MMEM:STOR:TRAC:FORM:SNP DB; *OPC?")
        self._read()

        # The SDATA assertion queries underlying real and imaginary pair data SDATA, dB FDATA
        # self._write('CALC' + str(channel) + ':DATA? FDATA')  # noqa: E800

        self._write(
            "CALC"
            + str(channel)
            + ':DATA:SNP:PORTs:Save "'
            + str(ports)
            + '", "'
            + str(file)
            + '"; *OPC?'
        )
        self._read()

    def read_power_sweep(self) -> str:
        """Read power sweep."""
        self._write("INITiate:CONTinuous OFF")
        self._write("INITiate:IMMediate; *wai")
        self._write("CALC:MEAS:RDATA? A; *OPC?")
        self._write("CALCulate:RDATA? REF; *OPC?")
        return self._read()

    def is_error(self) -> int:
        """Check the instrument to see if it has any errors in its queue."""
        raw_error = ""
        error_code = -1

        while error_code != 0:
            self._write("SYST:ERR?; *OPC?")
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

    def preset(self) -> None:
        """Preset the PNA and wait for preset completion via use of *OPC?.

        *OPC? holds-off subsequent commands and places a "1" on the output buffer
        when the predicating command functionality is complete. Do not use a loop
        with *OPC? as there is no change from a 0 condition to a 1 condition.
        A '1' is placed on the output buffer when the operation is complete.
        """
        self._write("SYST:PRES; *OPC?")
        self._read()

        # Clear the event status registers and empty the error queue
        self._write("*CLS")

    def close_connection(self) -> None:
        """Close the connection to the instrument."""
        self.close()

    def get_data_format(self) -> str:
        """Set data transfer format to ASCII."""
        self._write("FORM:DATA?")
        return self._read()

    def set_data_format_ascii(self) -> None:
        """Set data transfer format to ASCII."""
        self._write("FORM:DATA ASCII")

    def get_channel_type(self, channel: int = 1) -> str:
        """Get channel type."""
        channel_name = self._query("SENS" + str(channel) + ":CLAS:NAME?")
        return channel_name

    def get_IFBW(self, channel: int = 1) -> int:  # noqa: N802
        """Get IFBW."""
        return round(float(self._query("SENS" + str(channel) + ":BWID?")))

    def get_averaging(self, channel: int = 1) -> int:
        """Get averaging."""
        return round(float(self._query("SENS" + str(channel) + ":AVER:COUN?")))

    def set_averaging(self, averages: int = 4, channel: int = 1) -> None:
        """Set averaging."""
        self._write("SENS" + str(channel) + ":AVER:COUN " + str(averages))
        if averages > 1:
            self._write("SENS" + str(channel) + ":AVER ON")

    def average_restart(self, channel: int = 1) -> None:
        """Average restart."""
        self._write("SENS" + str(channel) + ":AVER:CLE")

    def set_trigger_source(self, source: str = "internal") -> None:
        """Set trigger source."""
        # self._write("CONT:SOUR " + str(source) + "; *OPC?")  # noqa: E800
        # opc = self._read()  # noqa: E800
        pass

    def set_sweep_trigger_mode(self, mode: str = "channel", channel: int = 1) -> None:
        """Set sweep trigger mode.

        Mode options include: channel, sweep, point, trace.
        """
        # self._write("SENS" + str(channel) + ":SWE:TRIG " + str(mode) + "; *OPC?")  # noqa: E800
        # self._read()  # noqa: E800
        pass

    def set_sweep_group_count(self, count: int = 1, channel: int = 1) -> None:
        """Set sweep group count."""
        self._write("SENS" + str(channel) + ":SWE:GRO:COUN " + str(count))

    def set_sparameters(self) -> None:
        """Set sparameters."""
        # Preset the PNA and wait for preset completion via use of *OPC?
        # *OPC? holds-off subsequent commands and places a "1" on the output buffer
        # when the predicating command functionality is complete. Do not use a loop
        # with *OPC? as there is no change from a 0 condition to a 1 condition.
        # A '1' is placed on the output buffer when the operation is complete.
        # self._write("SYST:PRES; *OPC?")  # noqa: E800
        self._write("SYST:FPRESET; *OPC?")
        self._read()

        self._write("INITiate1:CONTinuous OFF; *OPC?")
        # self._write("SENS:SWE:MODE SING; *OPC?")  # noqa: E800
        self._read()

        # Select the default measurement name as assigned on preset.
        # To catalog the measurement names, by channel number, use the
        # 'CALCulate[n]:PARameter:CATalog?' command where [n] is the channel
        # number. The channel number, n, defaults to "1" and is optional.
        # Measurement name is case sensitive.
        self._write("CALC:PAR:DEL:ALL; *OPC?")
        self._read()
        self._write("CALC:PAR:EXT 'CH1_S11', 'S1_1'")
        self._write("CALC:PAR:EXT 'CH1_S12', 'S1_2'")
        self._write("CALC:PAR:EXT 'CH1_S21', 'S2_1'")
        self._write("CALC:PAR:EXT 'CH1_S22', 'S2_2'")

        # Turn on window 1
        self._write("DISP:WIND1:STAT ON")

        # Place traces on window 1
        self._write("DISP:WIND1:TRAC1:FEED 'CH1_S11'")
        self._write("DISP:WIND1:TRAC2:FEED 'CH1_S12'")
        self._write("DISP:WIND1:TRAC3:FEED 'CH1_S21'")
        self._write("DISP:WIND1:TRAC4:FEED 'CH1_S22'")

        self._write("*OPC?")
        self._read()
        # self._write("CALC:PAR:MNUM 1")  # noqa: E800

        # Set data transfer format to ASCII  # noqa: E800
        # self._write("FORM:DATA ASCII")  # noqa: E800

        return

    def get_trace_measurement(self, trace_number: int = 1) -> list[float]:
        """Get trace measuerement."""
        averages = self.get_averaging()

        if averages > 1:
            self.average_restart(channel=1)

            self.set_sweep_group_count(count=averages, channel=1)
            self.set_sweep_mode(mode="GRO", channel=1)
        else:
            self.set_sweep_mode(mode="SINGLE", channel=1)

        self._write("FORM:DATA ASCII")
        self._write(f"CALC{1}:FORM: MLOG")
        self._write("*OPC?")
        self._read()

        self._write(f"CALC{1}:PAR:MNUM {trace_number}")
        # The SDATA assertion queries underlying real and imaginary pair data SDATA, dB FDATA
        self._write(f"CALC{1}:DATA? FDATA")
        s21_raw = self._read()

        s21_split = s21_raw.split(",")
        s21 = [float(elem) for elem in s21_split]

        return s21

    def set_power_sweep_parameters(self, direction: str = "normal", channel: int = 1) -> None:
        """Set power sweep parameters."""
        self._write("CALC:PAR:DEL:ALL; *OPC?")
        self._read()

        if direction == "normal":
            self._write("CALC:PAR:EXT 'CH1_S2_1', 'S2_1'")
            self._write("CALC:PAR:EXT 'CH1_R1_1', 'R1_1'")
            self._write("CALC:PAR:EXT 'CH1_B_1', 'B_1'")

            # Turn on window 1
            self._write("DISP:WIND1:STAT ON")

            # Place traces on window 1
            self._write("DISP:WIND1:TRAC1:FEED 'CH1_S2_1'")
            self._write("DISP:WIND1:TRAC2:FEED 'CH1_R1_1'")
            self._write("DISP:WIND1:TRAC3:FEED 'CH1_B_1'")

        else:
            self._write("CALC:PAR:EXT 'CH1_S1_2', 'S1_2'")
            self._write("CALC:PAR:EXT 'CH1_R2_2', 'R2_2'")
            self._write("CALC:PAR:EXT 'CH1_A_2', 'A_2'")

            # Turn on window 1
            self._write("DISP:WIND1:STAT ON")

            # Place traces on window 1
            self._write("DISP:WIND1:TRAC1:FEED 'CH1_S1_2'")
            self._write("DISP:WIND1:TRAC2:FEED 'CH1_R2_2'")
            self._write("DISP:WIND1:TRAC3:FEED 'CH1_A_2'")

            self._write("*OPC?")
            self._read()
        return

    def read_power_sweep_parameters(
        self, direction: str = "normal", channel: int = 1
    ) -> List[List[float]]:
        """Read power sweep parameters."""
        # Round all values this number of decimals
        decimals = 2

        averages = self.get_averaging()

        if averages > 1:
            # Restart averaging
            self.average_restart(channel=channel)

            # Group sweep equal to the number of averages
            self.set_sweep_group_count(count=averages, channel=channel)
            self.set_sweep_mode(mode="GRO", channel=channel)

        self._write("FORM:DATA ASCII")

        self._write("CALC" + str(channel) + ":FORM MLOG")
        self._write("*OPC?")
        self._read()

        self._write("CALC" + str(channel) + ":PAR:MNUM 3")
        # The SDATA assertion queries underlying real and imaginary pair data SDATA, dB FDATA

        self._write("CALC" + str(channel) + ":DATA? FDATA")
        s21 = self._read()
        self._write("*OPC?")
        self._read()
        s21_: List[str] = s21.split(",")
        s21__: List[float] = [round(float(i), decimals) for i in s21_]

        self._write("CALC" + str(channel) + ":PAR:MNUM 1")
        # The SDATA assertion queries underlying real and imaginary pair data SDATA, dB FDATA
        self._write("CALC" + str(channel) + ":DATA? FDATA")
        r11 = self._read()
        self._write("*OPC?")
        self._read()
        r11_: List[str] = r11.split(",")
        r11__: List[float] = [round(float(i), decimals) for i in r11_]

        self._write("CALC" + str(channel) + ":PAR:MNUM 2")
        # The SDATA assertion queries underlying real and imaginary pair data SDATA, dB FDATA
        self._write("CALC" + str(channel) + ":DATA? FDATA")
        b1: str = self._read()
        self._write("*OPC?")
        self._read()
        b1_: List[str] = b1.split(",")
        b1__: List[float] = [round(float(i), decimals) for i in b1_]

        params = [r11__, b1__, s21__]

        return params

    def read_sparameters_dB(self):  # type: ignore # noqa
        """Read sparameters dB."""
        # Turn continuous sweep off
        self._write("INITiate1:CONTinuous OFF; *OPC?")
        self._read()

        self._write("SENS1:SWE:TRIG:POIN OFF")

        self._write("INITiate1; *OPC?")
        self._read()

        self._write("FORM ASCII")

        self._write("CALC1:PAR:SEL 'CH1_S11'")

        # The SDATA assertion queries underlying real and imaginary pair data SDATA, dB FDATA
        self._write("CALC1:DATA? FDATA")
        s11 = self._read()
        s11 = s11.split(",")
        s11 = [float(i) for i in s11]

        self._write("CALC1:PAR:SEL 'CH1_S12'")

        # The SDATA assertion queries underlying real and imaginary pair data SDATA, dB FDATA
        self._write("CALC1:DATA? FDATA")
        s12 = self._read()
        s12 = s12.split(",")
        s12 = [float(i) for i in s12]

        self._write("CALC1:PAR:SEL 'CH1_S21'")

        # The SDATA assertion queries underlying real and imaginary pair data SDATA, dB FDATA
        self._write("CALC1:DATA? FDATA")
        s21 = self._read()
        s21 = s21.split(",")
        s21 = [float(i) for i in s21]

        self._write("CALC1:PAR:SEL 'CH1_S22'")

        # The SDATA assertion queries underlying real and imaginary pair data SDATA, dB FDATA
        self._write("CALC1:DATA? FDATA")
        s22 = self._read()
        s22 = s22.split(",")
        s22 = [float(i) for i in s22]

        # sparams = np.zeros((2,2,len(s11)),dtype=float)  # noqa: E800
        x = 2  # noqa: F841
        y = 2  # noqa: F841
        z = len(s11)
        # sparams = [[[0 for k in range(z)] for j in range(y)] for i in range(x)]  # noqa: E800

        sparams = [[[s11[k], s12[k]], [s21[k], s22[k]]] for k in range(z)]

        return sparams

    def get_measurement_list(self, channel: int = 1) -> List[str]:
        """Gets measurement list."""
        # measurement_list = self._query("CALC:PAR:CAT?")  # noqa: E800
        measurement: str = self._query("CALC" + str(channel) + ":PARameter:CATalog:EXTended?; *OPC")
        measurement = measurement.replace('"', "")
        measurement_list: List[str] = measurement.split(",")
        for i, item in enumerate(measurement_list):
            measurement_list[i] = item.replace("_", ",")
        return measurement_list

    def set_frequency_sweep(self, start: float, end: float, step: int) -> None:
        """Set frequency sweep."""
        points = round((end - start) / step) + 1
        self._write("SENS1:SWE:POIN " + str(points))
        self._write("SENS1:FREQ:STAR " + str(start))
        self._write("SENS1:FREQ:STOP " + str(end))

        self._write("*OPC?")
        self._read()

    def set_power_sweep(
        self, start: float, end: float, step: int, channel: int = 1, port: int = 1
    ) -> None:
        """Set power sweep."""
        # Set frequency sweep
        self._write("SOUR:POW:COUP OFF; *OPC?")
        self._read()

        points = round((end - start) / step) + 1
        self._write("SENS" + str(channel) + ":SWE:POIN " + str(points))
        self._write("SOUR:POW" + str(port) + ":STAR " + str(start))
        self._write("SOUR:POW" + str(port) + ":STOP " + str(end))
        # self._write("SENS:SWE:DWEL .1")  # noqa: E800

        self._write("*OPC?")
        self._read()

    def set_CW_frequency(self, freq: float = 1e9, channel: int = 1) -> str:  # noqa: N802
        """Set CW frequency."""
        self._write("SENS" + str(channel) + ":FREQ:CW " + str(freq) + "; *OPC?")
        return self._read()

    def get_sweep_points(self, channel: int = 1) -> int:
        """Get sweep points."""
        return round(float(self._query("SENS" + str(channel) + ":SWE:POIN?")))

    def set_sweep_points(self, points: int = 21, channel: int = 1) -> None:
        """Set sweep points."""
        self._write("SENS" + str(channel) + ":SWE:POIN " + str(points) + "; *OPC?")
        self._read()

    def get_power_level(self, port: int = 1) -> float:
        """Get power level."""
        return float(self._query("SOUR" + str(port) + ":POW?"))

    def get_start_power_level(self, port: int = 1) -> float:
        """Get start power level."""
        return float(self._query("SOUR:POW" + str(port) + ":STAR?"))

    def get_stop_power_level(self, port: int = 1) -> float:
        """Get stop power level."""
        return float(self._query("SOUR:POW" + str(port) + ":STOP?"))

    def set_linear_sweep_type(self) -> None:
        """Set linear sweep type."""
        self._write("SENSe1:SWEep:TYPE LIN; *OPC?")
        self._read()

    def set_power_sweep_type(self, channel: int = 1) -> None:
        """Set power sweep type."""
        self._write("SENS" + str(channel) + ":SWE:TYPE POW; *OPC?")
        self._read()

    def set_stepped_sweep(self) -> None:
        """Set stepped sweep."""
        self._write("SENS:SWE:GEN STEP; *OPC?")
        self._read()

    def set_analog_sweep(self) -> None:
        """Set analog sweep."""
        self._write("SENS:SWE:GEN ANA; *OPC?")
        self._read()

    def get_sweep_time(self) -> float:
        """Get sweep time."""
        # Query the sweep time
        return round(float(self._query("SENS:SWE:TIME?")), 6)

    def source_power_cal(self, port: int) -> None:
        """Performs a source power cal on channel 1 - port 1 using a USB power sensor."""
        # Performs a source power cal on channel 1 - port 1 using a USB power sensor
        # This example assumes ONE USB power sensor is connected to the PNA
        # Dim app
        # Dim scpi
        # Dim sensor
        # Create / Get the PNA application.
        # Set app = CreateObject("AgilentPNA835x.Application")
        # Set scpi = app.ScpiStringParser
        # scpi.parse "SYST:PRES"
        # set power accuracy tolerance and iterations
        self._write("SOUR1:POW1:CORR:COLL:ITER:NTOL 0.1")
        self._read()
        self._write("SOUR1:POW1:CORR:COLL:ITER:COUN 15")
        # set power sensor settling tolerance
        self._write("SOUR1:POW1:CORR:COLL:AVER:NTOL 0.1")
        self._write("SOUR1::POW1:CORR:COLL:AVER:COUN 15")
        # set offset value for amp or attenuation
        self._write("SOUR1:POW1:CORR:OFFS 0 DB")
        # show source power cal dialog
        self._write("SOUR1:POW1:CORR:COLL:DISP ON")
        # read the usb power sensor ID string
        sensor = self._query("SYST:COMM:USB:PMET:CAT?")
        # specify that sensor
        self._write("SYST:COMM:PSEN usb," + sensor)
        # do the measurement
        self._write('SOUR1:POW1:CORR:COLL:ACQ PMR,"ASENSOR"')
        # save the source cal and create an R-Channel response calset
        self._write("SOUR:POW:CORR:COLL:SAVE RREC")

    def save_distortion_table(self, channel: int, file: str = "measurement.csv") -> None:
        """Save Distortion Table to CSV file.

        Args:
            channel: Channel number to save table for.
            file: File name/path to save table to. Defaults to "measurement.csv".
        """
        self._write(f"SENS{channel}:DIST:TABLe:DISPlay:SAVE '{file}'")

    def transfer_file(self, filename: str) -> str:
        """Transfer file at PNAX over SCPI.

        # TODO: Could be moved to protocol?
        Args:
            filename: Path on instrument of file to transfer.

        Returns:
            File contents of filename as string
        """
        return self._query(f"MMEM:TRAN? '{filename}'")

    def make_directory(self, directory_path: str) -> None:
        """Make directory at directory_path on PNAX filesystem.

        Args:
            directory_path: Path of directory to make on self.
        """
        self._write(f"MMEM:MDIR '{directory_path}'")

    def setup_power_sweep(
        self,
        channel: int,
        trx_mode: str,
        power_sweep_start: float,
        power_sweep_stop: float,
        power_sweep_points: int,
        if_lo_rf_freq: tuple = (5, 23, 28),
    ) -> None:
        """Setup Power Sweep.

        Args:
            channel: Channel selection on PNA-X.
            trx_mode: Tx/Rx Mode of DUT.
            power_sweep_start: Power Sweep start level.
            power_sweep_stop: Power Sweep stop level.
            power_sweep_points: Power Sweep number of points.
            if_lo_rf_freq: IF, LO, RF frequencies (GHz).
        """
        if_freq = if_lo_rf_freq[0]
        lo_freq = if_lo_rf_freq[1]
        rf_freq = if_lo_rf_freq[2]

        if trx_mode == "RX":
            # Setup RX Power Sweep (MID BAND)
            self._write("SENSe" + str(channel) + ":MIXer:INPut:FREQuency:MODE fixed")
            self._write("SENSe" + str(channel) + f":MIXer:INPut:FREQuency:fixed {rf_freq}e9")
            self._write("SENSe" + str(channel) + ":MIXer:LO:FREQuency:MODE fixed")
            self._write("SENSe" + str(channel) + f":MIXer:LO:FREQuency:fixed {lo_freq}e9")
            self._write("SENSe" + str(channel) + ":MIXer:LO1:FREQ:ILTI 1")
            self._write("SENSe" + str(channel) + ":MIXer:OutPut:FREQuency:MODE fixed")
            self._write("SENSe" + str(channel) + ":MIXer:CALCulate output")
            self._write("SENS" + str(channel) + ":SWE:TYPE POW")
            self._write("SOUR" + str(channel) + ":POW4:ATT 20")
            self._write("SOUR" + str(channel) + f":POW4:STAR {power_sweep_start}")
            self._write("SOUR" + str(channel) + f":POW4:STOP {power_sweep_stop}")
            self._write("SENS" + str(channel) + ":MIX:LO1:POW:STAR 0")
            self._write("SENS" + str(channel) + ":MIX:LO1:POW:STOP 0")
            self._write("SENS" + str(channel) + f":SWE:POIN {power_sweep_points}")

        if trx_mode == "TX":
            # Setup TX Power Sweep (MID BAND)
            self._write("SENSe" + str(channel) + ":MIXer:INPut:FREQuency:MODE fixed")
            self._write("SENSe" + str(channel) + f":MIXer:INPut:FREQuency:fixed {if_freq}e9")
            self._write("SENSe" + str(channel) + ":MIXer:LO:FREQuency:MODE fixed")
            self._write("SENSe" + str(channel) + f":MIXer:LO:FREQuency:fixed {lo_freq}e9")
            self._write("SENSe" + str(channel) + ":MIXer:LO1:FREQ:ILTI 0")
            self._write("SENSe" + str(channel) + ":MIXer:OutPut:FREQuency:MODE fixed")
            self._write("SENSe" + str(channel) + ":MIXer:CALCulate output")
            self._write("SENS" + str(channel) + ":SWE:TYPE POW")
            self._write("SOUR" + str(channel) + ":POW3:ATT 20")
            self._write("SOUR" + str(channel) + f":POW3:STAR {power_sweep_start}")
            self._write("SOUR" + str(channel) + f":POW3:STOP {power_sweep_stop}")
            self._write("SENS" + str(channel) + ":MIX:LO1:POW:STAR 0")
            self._write("SENS" + str(channel) + ":MIX:LO1:POW:STOP 0")
            self._write("SENS" + str(channel) + f":SWE:POIN {power_sweep_points}")

    def setup_frequency_sweep(
        self,
        channel: int,
        trx_mode: str,
        if_lo_rf_freq: tuple = (5, 23, 28),
        freq_sweep_offset: float = 0.5,
        tx_power: float = -45,
        rx_power: float = -60,
    ) -> None:
        """Setup Frequency Sweep.

        Args:
            channel: Channel selection on PNA-X.
            trx_mode: Tx/Rx Mode of DUT.
            if_lo_rf_freq: IF, LO, RF frequencies (GHz).
            freq_sweep_offset: Range up and down from center frequency to sweep.
            tx_power: Default TX Power to run sweep at.
            rx_power: Default RX Power to run sweep at.
        """
        if_freq = if_lo_rf_freq[0]
        lo_freq = if_lo_rf_freq[1]
        rf_freq = if_lo_rf_freq[2]

        if trx_mode == "RX":
            # Setup RX Freq Sweep (MID BAND)
            self._write("SENS" + str(channel) + ":SWE:TYPE LIN")
            self._write("SENSe" + str(channel) + ":MIXer:INPut:FREQuency:MODE swept")
            self._write(
                "SENSe"
                + str(channel)
                + f":MIXer:INPut:FREQuency:start {rf_freq - freq_sweep_offset}e9"
            )
            self._write(
                "SENSe"
                + str(channel)
                + f":MIXer:INPut:FREQuency:stop {rf_freq + freq_sweep_offset}e9"
            )
            self._write("SENSe" + str(channel) + ":MIXer:LO:FREQuency:MODE swept")
            self._write(
                "SENSe"
                + str(channel)
                + f":MIXer:LO:FREQuency:start {lo_freq - freq_sweep_offset}e9"
            )
            self._write(
                "SENSe" + str(channel) + f":MIXer:LO:FREQuency:stop {lo_freq + freq_sweep_offset}e9"
            )
            self._write("SENSe" + str(channel) + ":MIXer:LO1:FREQ:ILTI 1")
            self._write("SENSe" + str(channel) + ":MIXer:OutPut:FREQuency:MODE fixed")

        if trx_mode == "TX":
            # Setup TX Freq Sweep (MID BAND)
            self._write("SENS" + str(channel) + ":SWE:TYPE LIN")
            self._write("SENSe" + str(channel) + ":MIXer:INPut:FREQuency:MODE fixed")
            self._write("SENSe" + str(channel) + f":MIXer:INPut:FREQuency:fixed {if_freq}e9")
            self._write("SENSe" + str(channel) + ":MIXer:LO:FREQuency:MODE swept")
            self._write(
                "SENSe"
                + str(channel)
                + f":MIXer:LO:FREQuency:start {lo_freq - freq_sweep_offset}e9"
            )
            self._write(
                "SENSe" + str(channel) + f":MIXer:LO:FREQuency:stop {lo_freq + freq_sweep_offset}e9"
            )
            self._write("SENSe" + str(channel) + ":MIXer:LO1:FREQ:ILTI 0")
            self._write("SENSe" + str(channel) + ":MIXer:OutPut:FREQuency:MODE swept")

        self._write("SENSe" + str(channel) + ":MIXer:CALCulate output")
        self._write("SOUR" + str(channel) + ":POW:COUPle OFF")
        self._write("SENSe" + str(channel) + ":MIXer:LO:POW 0")
        self._write("SOUR" + str(channel) + ":POW3:ATT:Auto Off")
        self._write("SOUR" + str(channel) + ":POW4:ATT:Auto Off")
        self._write("SOUR" + str(channel) + ":POW3:ATT 30")
        self._write("SOUR" + str(channel) + ":POW4:ATT 30")
        self._write("SOUR" + str(channel) + f":POW3 {tx_power}")
        self._write("SOUR" + str(channel) + f":POW4 {rx_power}")

    def get_trace_formatted(self, trace: str) -> tuple[list[float], list[float]]:
        """Get Formatted trace data (magnitude & phase).

        Args:
            trace: Trace label

        Returns:
            tuple of magnitude and phase sweep
        """
        self._write(f"CALCulate{trace}:PARameter:MNUMber:SELect {trace}")
        self._write(f"SENSe{trace}:SWEep:MODE SINGle")
        self._query("*OPC?")

        self._write(f"CALCulate{trace}:FORMat MLOGarithmic")
        magnitude = []
        for val in self._query(f"CALCulate{trace}:DATA? FDATa").split(","):
            if "+1+" in val:
                val = val.replace("+1+", "+", 1)
            elif "+1-" in val:
                val = val.replace("+1-", "-", 1)
            magnitude.append(float(val))

        self._write(f"CALCulate{trace}:FORMat UPHase")
        phase = [
            float(val) % 360 for val in self._query(f"CALCulate{trace}:DATA? FDATa").split(",")
        ]

        self._write(f"CALCulate{trace}:FORMat MLOGarithmic")

        return magnitude, phase
