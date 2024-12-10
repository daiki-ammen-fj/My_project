"""Module for Keysight N3300A Electronic Load Tester."""

from instrument_lib.utils import GPIBNumber
from instrument_lib.instruments.instrument import SCPIInstrument


class N3300A(SCPIInstrument):
    """Class for the Keysight N3300A Electronic Load Tester."""

    ACCEPTED_MODELS = [
        "N3300A",
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

    def clear_errors(self) -> None:
        """Clear errors."""
        self._write("*CLS")

    def set_voltage(self, channel: int, voltage: float) -> None:
        """Set voltage of N3300A for specified channel.

        Args:
            channel: The channel to set the voltage value on.
            voltage: The voltage value that the channel will be set to.
        """
        set_voltage_command: str = f"CHAN {channel};:VOLT {voltage}"
        self._write(set_voltage_command)

    def set_current(self, channel: int, current: float) -> None:
        """Set current of N3300A for specified channel.

        Args:
            channel: The channel to set the current value on.
            current: The current value the the channel will be set to.
        """
        set_current_command: str = f"CHAN {channel};:CURR {current}"
        self._write(set_current_command)

    def read_set_voltage(self, channel: int) -> float:
        """Read the voltage of a given channel.

        Args:
            channel: The channel to read the voltage from.

        Returns:
            Float representation of given channel voltage.
        """
        read_voltage_command: str = f"CHAN {channel};:VOLT?"
        read_voltage: float = float(self._query(read_voltage_command))
        return read_voltage

    def read_set_current(self, channel: int) -> float:
        """Reads the current of a given channel.

        Args:
            channel: The channel to read the current from.

        Returns:
            Float representation of given channel current.
        """
        read_current_command: str = f"CHAN {channel};:CURR?"
        read_current: float = float(self._query(read_current_command))
        return read_current

    def read_measured_voltage(self, channel: int) -> float:
        """Reads the measured voltage from load tester.

        Args:
            channel: The channel to read measured voltage from.

        Returns:
            Float representation of given channel measured voltage.
        """
        read_measured_voltage_command: str = f"CHAN {channel};:MEAS:VOLT?"
        read_measured_voltage: float = float(self._query(read_measured_voltage_command))
        return read_measured_voltage

    def read_measured_current(self, channel: int) -> float:
        """Read the measured current from the load tester.

        Args:
            channel: The channel to read measured current from.

        Returns:
            Float representationa of given channelm measured current.
        """
        read_measured_current_command: str = f"CHAN {channel};:MEAS:CURR?"
        read_measured_current: float = float(self._query(read_measured_current_command))
        return read_measured_current

    def set_input(self, channel: int, on: bool) -> None:
        """Sets input mode either on or off for given channel.

        Args:
            channel: The channel to set input mode on.
            on: Status to set input mode to, True for on, False for off.
        """
        input_status: str
        if on:
            input_status = "ON"
        else:
            input_status = "OFF"

        set_input_command: str = f"CHAN {channel};:INPUT {input_status}"
        self._write(set_input_command)

    def set_transient_mode(self, mode: str) -> None:
        """Sets operating mode of transient generator.

        Args:
            mode: The mode to set transient generator to. Valid options include "CONT", "PULS", "TOGG", "OFF".
        """
        set_transient_mode_command: str = f"TRAN:MODE {mode}"
        self._write(set_transient_mode_command)

    def set_transient_generator(self, status: str) -> None:
        """Turns transient generator on or off.

        Args:
            status: State to set transient generator to. Valid options include "ON" and "OFF".
        """
        set_transient_generator_command: str = f"TRAN {status}"
        self._write(set_transient_generator_command)

    def transient_generator_on(self) -> None:
        """Turns transient generator on."""
        self.set_transient_generator("ON")

    def transient_generator_off(self) -> None:
        """Turns transient generator off."""
        self.set_transient_generator("OFF")
