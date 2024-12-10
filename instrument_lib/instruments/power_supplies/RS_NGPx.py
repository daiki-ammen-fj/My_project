"""Instrument Driver for RS_PS_NGP800."""

from typing import Dict, List, Optional, Union
from instrument_lib.utils import GPIBNumber
from instrument_lib.instruments.instrument import SCPIInstrument


class SenseState:
    """Utility class to represent sensor states.

    AUTO: If remote sense detection is set AUTO, the detection and enabling of the voltage sense
    relay automatically kicks in when the connection of remote sense wires (S+, S-) to the input
    of the load is applied.

    EXT: If remote sense detection is set EXT, internal voltage sense relay in the instrument is
    switched on and the connection of remote sense wires (S+, S- ) to the input of the load become
    necessary. Failure to connect remote sense can cause overvoltage or unregulated voltage output
    from the R&S NGP800.

    """

    POSSIBLE_STATES: List[str] = ["AUTO", "EXT"]

    def __init__(self, state: str):
        """Constructor.

        :param state: String for sensor state. Should be in ['AUTO', 'EXT']
        """
        if state not in self.POSSIBLE_STATES:
            raise ValueError(f"Invalid state supplied. Must be in {self.POSSIBLE_STATES}")

        self.state: str = state

    def __str__(self) -> str:
        """String representation."""
        return self.state


class Channel:
    """Utility class to represent channel state."""

    POSSIBLE_CHANNELS = [1, 2, 3, 4]

    def __init__(self, channel: int):
        """Constructor.

        :param channel: int for channel state. Should be in [1, 2, 3, 4]
        """
        if channel not in self.POSSIBLE_CHANNELS:
            raise ValueError(f"Invalid channel supplied. Must be in: {self.POSSIBLE_CHANNELS}")

        self.value: int = channel

    def __str__(self) -> str:
        """String representation."""
        return str(self.value)

    def __int__(self) -> int:
        """Integer representation."""
        return self.value


class VoltageSwitch:
    """Utility class to represent voltage switch."""

    POSSIBLE_VOLTAGES: List[int] = [0, 1]

    def __init__(self, voltage_switch: float):
        """Constructor.

        :param state: int for voltage switch state. Should be 0 or 1.
        """
        if int(voltage_switch) not in self.POSSIBLE_VOLTAGES:
            raise ValueError(f"Invalid channel supploed. Must be in: {self.POSSIBLE_VOLTAGES}")

        self.state: int = int(voltage_switch)

    def __str__(self) -> str:
        """String representation."""
        return str(self.state)


class RS_NGPx(SCPIInstrument):  # noqa
    """Power Supply class for RS_PS_NGP800.

    All operations within this class can raise InstrumentError (or a subclass).
    """

    ACCEPTED_MODELS = [
        "NGP814",
        "NGP804",
    ]

    DEFUALT_SENSE_STATE = SenseState("EXT")

    def __init__(
        self,
        gpib: GPIBNumber | None = None,
        ip_address: str | None = None,
        usb: tuple[str, str, str] | None = None,
        wireless: bool = False,
        simulate: bool = False,
        machine_num: int = 1,
    ):
        """Constructor.

        :param ip_address: IP Address of device as string.
        :param simulate: Flag to simulate in instrument.
        :param machine_num: Machine number.
        """
        super().__init__(gpib, ip_address, usb, wireless, simulate)
        self.channels: List[int] = [1, 2, 3, 4]
        self.switch_options: List[int] = [1, 0]
        self.machine_id: int = machine_num
        self.retry = 100
        self.rsinstrument = True

    def on(self, channel: Union[str, int] = "ALL") -> None:
        """Turn on power supply."""
        if channel == "ALL":
            self._write("OUTPUT:STATE 1, (@1:4)")
        elif channel == 1:
            self._write("OUTPUT:STATE 1, (@1)")
        elif channel == 2:
            self._write("OUTPUT:STATE 1, (@2)")
        elif channel == 3:
            self._write("OUTPUT:STATE 1, (@3)")
        elif channel == 4:
            self._write("OUTPUT:STATE 1, (@4)")
        else:
            self._write("OUTPUT:STATE 1, (@%s)" % channel)

    def off(self, channel: Union[str, int] = "ALL") -> None:
        """Turn off power supply."""
        if channel == "ALL":
            self._write("OUTPUT:STATE 0, (@1:4)")
        elif channel == 1:
            self._write("OUTPUT:STATE 0, (@1)")
        elif channel == 2:
            self._write("OUTPUT:STATE 0, (@2)")
        elif channel == 3:
            self._write("OUTPUT:STATE 0, (@3)")
        elif channel == 4:
            self._write("OUTPUT:STATE 0, (@4)")
        else:
            self._write("OUTPUT:STATE 0, (@%s)" % channel)

    def reset(self) -> None:
        """Reset instrument."""
        self._write("*RST")

    def setup_machine(self, data_dict: Dict[int, Dict[str, Union[float, str]]]) -> None:
        """Helper function to setup machine according to settings in data_dict.

        :param data_dict: Dictionary of settings used to setup the machine.
        """
        for i in range(1, 5):
            self.set_voltage(channel=int(Channel(i)), voltage=float(data_dict[i]["voltage"]))
            self.set_current(int(Channel(i)), float(data_dict[i]["current"]))
            self.set_remote_sense(Channel(i), SenseState(str(data_dict[i]["remote_sense"])))
            self.toggle_ovp_state(Channel(i), VoltageSwitch(float(data_dict[i]["OVP_state"])))
            self.set_ovp_value(Channel(i), float(data_dict[i]["OVP_value"]))
            self.toggle_ocp_state(Channel(i), VoltageSwitch(float(data_dict[i]["OCP_state"])))
            self.set_ocp_delay(Channel(i), float(data_dict[i]["OCP_fuse_delay"]))
            self.toggle_opp_state(Channel(i), VoltageSwitch(float(data_dict[i]["OPP_state"])))
            self.set_opp_level(Channel(i), float(data_dict[i]["OPP_value"]))
            self.set_upper_voltage_limit(Channel(i), float(data_dict[i]["upp_volt_limit"]))
            self.set_upper_current_limit(Channel(i), float(data_dict[i]["upp_curr_limit"]))
            self.set_limit_state(Channel(i), VoltageSwitch(float(data_dict[i]["limit_state"])))
            self.toggle_output_delay_state(
                Channel(i), VoltageSwitch(float(data_dict[i]["out_del_state"]))
            )
            self.toggle_output_delay_duration(Channel(i), float(data_dict[i]["delay_multiplier"]))

    def get_settings(self) -> Dict[int, Dict[str, Union[float, str]]]:
        """Gets the settings currently used on the machine.

        :return: Dictionary of settings.
        """
        data_dict: Dict[int, Dict[str, Union[float, str]]] = {
            1: {},
            2: {},
            3: {},
            4: {},
        }
        for i in range(1, 5):
            data_dict[i]["voltage"] = self.get_voltage(int(Channel(i)))
            data_dict[i]["current"] = self.get_current(int(Channel(i)))
            data_dict[i]["remote_sense"] = self.get_remote_sense(Channel(i))
            data_dict[i]["OVP_state"] = self.get_ovp_state(Channel(i)).state
            data_dict[i]["OVP_value"] = self.get_ovp_value(Channel(i))
            data_dict[i]["OCP_state"] = self.get_ocp_state(Channel(i)).state
            data_dict[i]["OCP_fuse_delay"] = self.get_ocp_delay(Channel(i))
            data_dict[i]["OPP_state"] = self.get_opp_state(Channel(i)).state
            data_dict[i]["OPP_value"] = self.get_opp_level(Channel(i))
            data_dict[i]["upp_volt_limit"] = self.get_upper_voltage_limit(Channel(i))
            data_dict[i]["upp_curr_limit"] = self.get_upper_current_limit(Channel(i))
            data_dict[i]["limit_state"] = self.get_limit_state(Channel(i)).state
            data_dict[i]["out_del_state"] = self.get_output_delay_state(Channel(i)).state
            data_dict[i]["delay_multiplier"] = self.get_output_delay_duration(Channel(i))

        return data_dict

    def read_voltage(self, channel: Channel) -> float:
        """Queries the currently measured voltage of the selected channel.

        :param channel: A number 1-4 will select the channel that the
                                currently measured voltage gets queried from.
        :return: The currently measured voltage value.
        """
        voltage: str = self._query(f"MEAS:VOLT? (@{channel})")
        return float(voltage)

    def get_voltage(self, channel: int) -> float:
        """Queries the voltage value set for the selected channel.

        :param channel: A number 1-4 will select the channel that the
                                currently measured voltage gets queried from.
        :return: The set voltage value.
        """
        voltage: str = self._query(f"VOLT? (@{channel})")
        return float(voltage)

    def set_voltage(self, voltage: float, channel: int) -> None:
        """Sets the voltage value of the selected channel.

        :param channel: A number 1-4 will select the channel that the
                                currently measured voltage gets queried from.
        :param voltage: Numeric value to set voltage to.
        """
        self._write(f"VOLT {voltage}, (@{channel})")

    def read_current(self, channel: Channel) -> float:
        """Queries the currently measured current of the selected channel.

        :param channel: A number 1-4 will select the channel that the
                                currently measured voltage gets queried from.
        :return: The currently measured current.
        """
        current: str = self._query(f"MEAS:CURR? (@{channel})")
        return float(current)

    def get_current(self, channel: int) -> float:
        """Queries the Current value of the selected channel.

        :param channel: A number 1-4 will select the channel that the
                                currently measured voltage gets queried from.
        :return: The set current value.
        """
        current: str = self._query(f"CURR? (@{channel})")
        return float(current)

    def set_current(self, channel: int, current: float) -> None:
        """Sets the current value of the selected channel.

        :param channel: A number 1-4 will select the channel that the
                                currently measured voltage gets queried from.
        :param current: Numeric value (nonnegative) to set current to.
        """
        if current < 0:
            raise ValueError("Invalid current. Current must be nonnegative.")

        self._write(f"CURR {current}, (@{channel})")

    def get_remote_sense(self, channel: Channel) -> str:
        """Queries the remote sense detection of the selected channel.

        :param channel: A number 1-4 will select the channel that the
                                currently measured voltage gets queried from.
        :return: 'AUTO' or 'EXT'
        """
        sensor: str = self._query(f"VOLT:SENS? (@{channel})")
        return sensor[:-1]

    def set_remote_sense(
        self, channel: Channel, sense_state: SenseState = DEFUALT_SENSE_STATE
    ) -> None:
        """Sets the remote sense detection of the selected channel.

        :param channel: A number 1-4 will select the channel that the
                                currently measured voltage gets queried from.
        :param sense_state: Defaults to EXT.
        """
        self._write(f"VOLT:SENS:SOUR {sense_state} (@{channel})")

    def toggle_ovp_state(self, channel: Channel, switch: VoltageSwitch) -> None:
        """Sets the OCP (Over Voltage Protection) of the selected channel.

        :param channel: A number 1-4 will select the channel that the
                                currently measured voltage gets queried from.
        :param switch: 1 will activate OVP, 0 will deactivate OVP

        """
        self._write(f"VOLT:PROT {switch}, (@{channel})")

    def get_ovp_state(self, channel: Channel) -> VoltageSwitch:
        """Queries the OVP (Over Voltage Protection) of the selected channel.

        :param channel: A number 1-4 will select the channel that the
                                currently measured voltage gets queried from.
        :return: 1 is activated OVP, 0 is deactivated OVP
        """
        ovp_state = self._query(f"VOLT:PROT? (@{channel})")
        return VoltageSwitch(int(ovp_state))

    def set_ovp_value(self, channel: Channel, voltage_protection_num: float) -> None:
        """Sets the OVP value of the selected channel.

        :param channel: A number 1-4 will select the channel that the
                                currently measured voltage gets queried from.
        :param voltage_protection_num: The numeric value of the OVP will get set to.
        """
        self._write(f"VOLT:PROT:LEV {voltage_protection_num}, (@{channel})")

    def get_ovp_value(self, channel: Channel) -> float:
        """Queries the OVP value of the selected channel.

        :param channel: A number 1-4 will select the channel that the
                                currently measured voltage gets queried from.
        :return: Numeric value of the OVP value in Volts.
        """
        ovp_value: str = self._query(f"VOLT:PROT:LEV? (@{channel})")
        return float(ovp_value)

    def toggle_ocp_state(self, channel: Channel, switch: VoltageSwitch) -> None:
        """Sets the OCP (Over Current Protection) state of the selected channel.

        :param channel: A number 1-4 will select the channel that the
                                currently measured voltage gets queried from.
        :param switch: Value of 1 will activate OCP, value of 0 will deactivate it.
        """
        self._write(f"FUSE {switch}, (@{channel})")

    def get_ocp_state(self, channel: Channel) -> VoltageSwitch:
        """Queries the OCP state of the selected channel.

        :param channel: A number 1-4 will select the channel that the
                                currently measured voltage gets queried from.
        :return: 1 is activated OCP, 0 is deactivated OCP.
        """
        ocp_state = self._query(f"FUSE? (@{channel})")
        return VoltageSwitch(int(ocp_state))

    def set_ocp_delay(self, channel: Channel, delay_time: float) -> None:
        """Sets the OCP delay time of the selected channel.

        :param channel: A number 1-4 will select the channel that the
                                currently measured voltage gets queried from.
        :param delay_time: The numeric fuse delay time value.
        """
        self._write(f"FUSE:DEL {delay_time}, (@{channel})")

    def get_ocp_delay(self, channel: Channel) -> float:
        """Queries the fuse deflay time at the selected channel.

        :param channel: A number 1-4 will select the channel that the
                                currently measured voltage gets queried from.
        :return: Numeric value for the set fuse delay time.
        """
        ocp_delay: str = self._query(f"FUSE:DEL? (@{channel})")
        return float(ocp_delay)

    def toggle_opp_state(self, channel: Channel, switch: VoltageSwitch) -> None:
        """Sets the OPP (Over Power Protection) state of the selected channel.

        :param channel: A number 1-4 will select the channel that the
                                currently measured voltage gets queried from.
        :param switch: 1 will activate OPP, 0 will deactivate OPP
        """
        self._write(f"POW:PROT {switch}, (@{channel})")

    def get_opp_state(self, channel: Channel) -> VoltageSwitch:
        """Queries the OPP state of the selected channel.

        :param channel: A number 1-4 will select the channel that the
                                currently measured voltage gets queried from.
        :return: 1 is activated OPP, 0 is deactivated OPP
        """
        opp_state: str = self._query(f"POW:PROT? (@{channel})")
        return VoltageSwitch(int(opp_state))

    def set_opp_level(self, channel: Channel, power_protection_num: float) -> None:
        """Sets the OPP value of the selected channel.

        :param channel: A number 1-4 will select the channel that the
                                currently measured voltage gets queried from.
        :param power_protection_num: The numeric value that the OPP will get set to.
        """
        # TODO: Should we check for valid power_protection_num?
        self._write(f"POW:PROT:LEV {power_protection_num}, (@{channel})")

    def get_opp_level(self, channel: Channel) -> float:
        """Queries the OPP value of the selected channel.

        :param channel: A number 1-4 will select the channel that the
                                currently measured voltage gets queried from.
        :return: Numeric value of the power protection level in Watts.
        """
        opp_power_level: str = self._query(f"POW:PROT:LEV? (@{channel})")
        return float(opp_power_level)

    def set_upper_voltage_limit(self, channel: Channel, voltage: float) -> None:
        """Sets the upper safety limit for voltage of the selected channel.

        :param channel: A number 1-4 will select the channel that the
                                currently measured voltage gets queried from.
        :param voltage: Numeric value for upper safety limit in Volts.
        """
        # TODO: Should we check for valid voltage_num?
        self._write(f"VOLT:ALIM:UPP {voltage}, (@{channel})")

    def get_upper_voltage_limit(self, channel: Channel) -> float:
        """Queries the upper safety limit for voltage of the selected channel.

        :param channel: A number 1-4 will select the channel that the
                                currently measured voltage gets queried from.
        :return: Numeric value for upper safety voltage limit in Volts.
        """
        voltage_limit: str = self._query(f"VOLT:ALIM:UPP? (@{channel})")
        return float(voltage_limit)

    def set_limit_state(self, channel: Channel, switch: VoltageSwitch) -> None:
        """Sets the safety limit state.

        :param channel: A number 1-4 will select the channel that the
                                currently measured voltage gets queried from.
        :param switch: 1 will activate the safety limit, 0 deactivates the safety limit.
        """
        self._write(f"ALIM {switch}, (@{channel})")

    def get_limit_state(self, channel: Channel) -> VoltageSwitch:
        """Gets the safety limit state.

        :param channel: A number 1-4 will select the channel that the
                                currently measured voltage gets queried from.
        :param switch: 1 is active safety limit, 0 is deactivate safety limit.
        """
        state_val: str = self._query(f"ALIM? (@{channel})")
        return VoltageSwitch(int(state_val))

    def set_upper_current_limit(self, channel: Channel, current: float) -> None:
        """Sets the upper safety limit for current of the selected channel.

        :param channel: A number 1-4 will select the channel that the
                                currently measured voltage gets queried from.
        :param current: Numeric current value for upper safety limit.
        """
        # TODO: Should we validate current?
        self._write(f"CURR:ALIM:UPP {current}, (@{channel})")

    def get_upper_current_limit(self, channel: Channel) -> float:
        """Gets the value of the upper safety limit for current of the selected channel.

        :param channel: A number 1-4 will select the channel that the
                                currently measured voltage gets queried from.
        :return: Numeric current value for upper safety limit.
        """
        current_limit: str = self._query(f"CURR:ALIM:UPP? (@{channel})")
        return float(current_limit)

    def toggle_channel_output_state(self, channel: Channel, switch: VoltageSwitch) -> None:
        """Sets the output state of the selected channel.

        :param channel: A number 1-4 will select the channel that the
                                currently measured voltage gets queried from.
        :param switch: 1 will activate output state, 0 will deactivate output state
        """
        self._write(f"OUTP:SEL {switch}, (@{channel})")

    def get_channel_output_state(self, channel: Channel) -> VoltageSwitch:
        """Queries the output state of the selected channel.

        :param channel: A number 1-4 will select the channel that the
                                currently measured voltage gets queried from.
        :return: 1 is active output for selected channel, 0 is deactivated output for channel.
        """
        output: str = self._query(f"OUTP:SEL? (@{channel})")
        return VoltageSwitch(int(output))

    def toggle_output_delay_state(self, channel: Channel, switch: VoltageSwitch) -> None:
        """Sets the output delay state of the selected channel.

        :param channel: A number 1-4 will select the channel that the
                                currently measured voltage gets queried from.
        :param switch: 1 will activate output delay, 0 will deactivate output delay.
        """
        self._write(f"OUTP:DEL {switch}, (@{channel})")

    def get_output_delay_state(self, channel: Channel) -> VoltageSwitch:
        """Queries the output delay state of the selected channel.

        :param channel: A number 1-4 will select the channel that the
                                currently measured voltage gets queried from.
        :return: 1 is active output delay, 0 is deactivated output delay.
        """
        output: str = self._query(f"OUTP:DEL? (@{channel})")
        return VoltageSwitch(int(output))

    def toggle_output_delay_duration(self, channel: Channel, time_delay: float) -> None:
        """Sets the duration for output delay of the selected channel.

        :param channel: A number 1-4 will select the channel that the
                                currently measured voltage gets queried from.
        :param time_delay: Numeric value of the duration in seconds.
        """
        self._write(f"OUTP:DEL:DUR {time_delay},(@{channel})")

    def get_output_delay_duration(self, channel: Channel) -> float:
        """Queries the duration for output delay of the selected channel.

        :param channel: A number 1-4 will select the channel that the
                                currently measured voltage gets queried from.
        :return: Numeric value of the duration in seconds.
        """
        output: str = self._query(f"OUTP:DEL:DUR? (@{channel})")
        return float(output)

    def toggle_master_output_state(self, switch: VoltageSwitch) -> None:
        """Sets the master output state (output button on machine).

        Even with channels on, machine won't run unless this function is activated.
        :param switch: 1 will activate the master switch, 0 will deactivate it.
        """
        self._write(f"OUTP:GEN {switch}")

    def get_master_output_state(self) -> VoltageSwitch:
        """Queries the master output state.

        :return: 1 will activate the master switch, 0 will deactivate it.
        """
        output: str = self._query("OUTP:GEN?")
        return VoltageSwitch(int(output))


POWER_PRESET_1: Dict[str, Dict[str, Union[float, str]]] = {
    "1": {
        "voltage": 1,
        "current": 20,
        "limit_state": 1,
        "upp_volt_limit": 1.2,
        "upp_curr_limit": 20,
        "remote_sense": "EXT",
        "OCP_state": 1,
        "OCP_fuse_delay": 0.2,
        "OVP_state": 1,
        "OVP_value": 1.25,
        "OPP_state": 0,
        "OPP_value": 10,
        "out_del_state": 1,
        "delay_multiplier": 0.1,
    },
    "2": {
        "voltage": 1.7,
        "current": 5,
        "limit_state": 1,
        "upp_volt_limit": 1.85,
        "upp_curr_limit": 6,
        "remote_sense": "EXT",
        "OCP_state": 1,
        "OCP_fuse_delay": 0.2,
        "OVP_state": 1,
        "OVP_value": 1.9,
        "OPP_state": 0,
        "OPP_value": 10,
        "out_del_state": 1,
        "delay_multiplier": 0.1,
    },
    "3": {
        "voltage": 3.3,
        "current": 3,
        "limit_state": 1,
        "upp_volt_limit": 3.5,
        "upp_curr_limit": 4,
        "remote_sense": "EXT",
        "OCP_state": 1,
        "OCP_fuse_delay": 0.2,
        "OVP_state": 1,
        "OVP_value": 3.8,
        "OPP_state": 0,
        "OPP_value": 10,
        "out_del_state": 1,
        "delay_multiplier": 0.1,
    },
    "4": {
        "voltage": 24,
        "current": 4,
        "limit_state": 1,
        "upp_volt_limit": 25,
        "upp_curr_limit": 6,
        "remote_sense": "AUTO",
        "OCP_state": 1,
        "OCP_fuse_delay": 0.2,
        "OVP_state": 1,
        "OVP_value": 25.5,
        "OPP_state": 0,
        "OPP_value": 10,
        "out_del_state": 1,
        "delay_multiplier": 0.1,
    },
}

POWER_PRESET_2: Dict[str, Dict[str, Union[float, str]]] = {
    "1": {
        "voltage": 1,
        "current": 20,
        "limit_state": 1,
        "upp_volt_limit": 1.2,
        "upp_curr_limit": 20,
        "remote_sense": "EXT",
        "OCP_state": 1,
        "OCP_fuse_delay": 0.2,
        "OVP_state": 1,
        "OVP_value": 1.25,
        "OPP_state": 0,
        "OPP_value": 10,
        "out_del_state": 1,
        "delay_multiplier": 0.1,
    },
    "2": {
        "voltage": 1.7,
        "current": 5,
        "limit_state": 1,
        "upp_volt_limit": 1.85,
        "upp_curr_limit": 6,
        "remote_sense": "EXT",
        "OCP_state": 1,
        "OCP_fuse_delay": 0.2,
        "OVP_state": 1,
        "OVP_value": 1.9,
        "OPP_state": 0,
        "OPP_value": 10,
        "out_del_state": 1,
        "delay_multiplier": 0.1,
    },
    "3": {
        "voltage": 3.3,
        "current": 3,
        "limit_state": 1,
        "upp_volt_limit": 3.5,
        "upp_curr_limit": 4,
        "remote_sense": "EXT",
        "OCP_state": 1,
        "OCP_fuse_delay": 0.2,
        "OVP_state": 1,
        "OVP_value": 3.8,
        "OPP_state": 0,
        "OPP_value": 10,
        "out_del_state": 1,
        "delay_multiplier": 0.1,
    },
    "4": {
        "voltage": 14,
        "current": 2,
        "limit_state": 1,
        "upp_volt_limit": 16,
        "upp_curr_limit": 2.5,
        "remote_sense": "AUTO",
        "OCP_state": 1,
        "OCP_fuse_delay": 0.2,
        "OVP_state": 1,
        "OVP_value": 18,
        "OPP_state": 0,
        "OPP_value": 10,
        "out_del_state": 1,
        "delay_multiplier": 0.1,
    },
}

POWER_PRESET_3: Dict[str, Dict[str, Union[float, str]]] = {
    "1": {
        "voltage": 1,
        "current": 15,
        "limit_state": 1,
        "upp_volt_limit": 1.3,
        "upp_curr_limit": 20,
        "remote_sense": "EXT",
        "OCP_state": 1,
        "OCP_fuse_delay": 0.2,
        "OVP_state": 1,
        "OVP_value": 1.2,
        "OPP_state": 0,
        "OPP_value": 10,
        "out_del_state": 1,
        "delay_multiplier": 0.1,
    },
    "2": {
        "voltage": 1,
        "current": 15,
        "limit_state": 1,
        "upp_volt_limit": 1.2,
        "upp_curr_limit": 20,
        "remote_sense": "EXT",
        "OCP_state": 1,
        "OCP_fuse_delay": 0.2,
        "OVP_state": 1,
        "OVP_value": 5.5,
        "OPP_state": 0,
        "OPP_value": 10,
        "out_del_state": 1,
        "delay_multiplier": 0.1,
    },
    "3": {
        "voltage": 1.7,
        "current": 5,
        "limit_state": 1,
        "upp_volt_limit": 1.9,
        "upp_curr_limit": 7,
        "remote_sense": "EXT",
        "OCP_state": 1,
        "OCP_fuse_delay": 0.2,
        "OVP_state": 1,
        "OVP_value": 5.5,
        "OPP_state": 0,
        "OPP_value": 10,
        "out_del_state": 1,
        "delay_multiplier": 0.1,
    },
    "4": {
        "voltage": 3.3,
        "current": 2,
        "limit_state": 1,
        "upp_volt_limit": 3.5,
        "upp_curr_limit": 2.5,
        "remote_sense": "EXT",
        "OCP_state": 1,
        "OCP_fuse_delay": 0.2,
        "OVP_state": 1,
        "OVP_value": 3.5,
        "OPP_state": 0,
        "OPP_value": 10,
        "out_del_state": 1,
        "delay_multiplier": 0.1,
    },
}
