"""Instrument class."""

from abc import ABC, abstractmethod
from typing import cast, Optional, Type, Union, Protocol, runtime_checkable
from time import sleep

from pyvisa import ResourceManager
import pyvisa.errors
from pyvisa.resources import (
    GPIBInstrument,
    TCPIPInstrument,
    TCPIPSocket,
    USBInstrument,
    SerialInstrument,
)
from RsInstrument import ResourceError, RsInstrument, StatusException

from instrument_lib.utils import (
    ConnectError,
    GPIBNumber,
    InstrumentError,
    InstrumentIdentificationInfo,
)


@runtime_checkable
class Instrument(Protocol):
    """Base class for higher level instrument classes to use."""

    identification: InstrumentIdentificationInfo

    def connect(self) -> None:
        """Deriving classes should implement connect."""
        ...

    def close(self) -> None:
        """Deriving classes should implement close."""
        ...

    def identify(self) -> InstrumentIdentificationInfo:
        """Instrument identification."""
        ...


class SCPIInstrument(Instrument):
    """Wrapper for higher level instrument classes to connect to."""

    def __init__(
        self,
        gpib: GPIBNumber | None = None,
        ip_address: str | None = None,
        usb: tuple[str, str, str] | None = None,
        wireless: bool = False,
        simulate: bool = False,
        serial_instrument_port: str | int | None = None,
        serial_instrument_baudrate: int | None = None,
    ):
        """Initializes instrument.

        :param gpib: GPIB number, [1, 31].
        :param ip_address: IP Address as string.
        :param wireless: Flag for wireless instrument.
        :param simulate: Flag to simulate in instrument.
        :param serial_instrument_port: If connecting through serial port. string on linux, int on windows.
        :param serial_instrument_baudrate: Desired baudrate if connecting through serial instrument port.

        :raises ConnectionError: Connection to instrument hardware failed.
        :raises ValueError: Invalid arguments suppplied.
        """
        super().__init__()
        self.gpib = gpib
        self.ip_address = ip_address
        self.usb = usb
        self.wireless = wireless
        self.simulate = simulate
        self.serial_instrument_port = serial_instrument_port
        self.serial_instrument_baudrate = serial_instrument_baudrate
        self.instrument: GPIBInstrument | RsInstrument | SerialInstrument = None

    def connect(self) -> None:  # noqa: C901
        """Connect instrument class to physical instrument."""
        try:
            is_rsinstrument: bool = self.rsinstrument  # type: ignore
        except AttributeError:
            is_rsinstrument = False

        if is_rsinstrument:
            self._connect_rs_instrument()

        elif self.gpib:
            self._connect_gpib()
            self.instrument.clear()

        elif self.ip_address:
            self._connect_ip()
            self.instrument.clear()

        elif self.usb:
            self._connect_usb()
            self.instrument.clear()

        elif self.serial_instrument_port:
            self._connect_asrl_instrument()
            # Removed .clear from this for now, was breaking DC310S functionality.

        else:
            raise ValueError("No valid GPIB Number or IP address supplied.")

        self.connected = True
        self.identify()  # type: ignore

    def _connect_rs_instrument(self) -> None:
        open_resource_command = f"TCPIP::{self.ip_address}::INSTR"
        optional_simulate_command: Optional[str] = "Simulate=True" if self.simulate else None
        try:
            resource = RsInstrument(
                open_resource_command,
                True,
                False,
                options=optional_simulate_command,
            )
        except ResourceError as e:
            raise ConnectError from e
        else:
            self.instrument = resource
            self.instrument_type: Type = RsInstrument

    def _connect_gpib(self) -> None:
        open_resource_command = (
            f"gpib1::{self.gpib}::instr" if self.wireless else f"GPIB0::{self.gpib}::INSTR"
        )
        # pyvsisa_backend = "@sim" if self.simulate else "@py"
        # Currently no py-visa-py backend. Using gpib with pyvisa-py backend requires additional packages.
        # TODO Add support for py-visa-py backend.
        resource_manager = ResourceManager()

        try:
            resource = cast(
                GPIBInstrument,
                resource_manager.open_resource(open_resource_command),
            )
        except Exception as e:
            raise ConnectError from e
        else:
            if not resource:
                raise ConnectError("Failed to connect to instrument.")

            self.instrument = resource
            self.instrument_type = GPIBInstrument

    def _connect_usb(self) -> None:
        if self.usb is None:
            raise ValueError("Attempting to connect with USB but no USB connection data.")
        open_resource_command = f"USB0::{self.usb[0]}::{self.usb[1]}::{self.usb[2]}::INSTR"
        # No pyvisa-py backend. Using USB w/o pyvisa-py backend requires that a VISA.dll is installed.
        # TODO: Add support for installing pyusb and libusb so that pyvisa-py works.
        resource_manager = ResourceManager()

        try:
            resource = cast(USBInstrument, resource_manager.open_resource(open_resource_command))
        except Exception as e:
            raise ConnectError from e
        else:
            if not resource:
                raise ConnectError("Failed to connect to instrument.")

            self.instrument = resource
            self.instrument_type = USBInstrument

    def _connect_ip(self) -> None:
        open_resource_command = f"TCPIP::{self.ip_address}::inst0::INSTR"
        pyvsisa_backend = "@sim" if self.simulate else "@py"
        resource_manager = ResourceManager(pyvsisa_backend)

        try:
            resource = cast(
                TCPIPInstrument,
                resource_manager.open_resource(
                    open_resource_command,
                ),
            )

        except ResourceError as e:
            raise ConnectError from e
        else:
            self.instrument = resource
            self.instrument_type = TCPIPInstrument

    def _connect_asrl_instrument(self) -> None:
        """Handles connecting to standard serial instruments."""
        open_resource_command: str = f"ASRL{self.serial_instrument_port}::INSTR"
        pyvisa_backend: str = "@sim" if self.simulate else "@py"
        resource_manager: ResourceManager = ResourceManager(pyvisa_backend)

        try:
            resource: SerialInstrument = cast(
                SerialInstrument, resource_manager.open_resource(open_resource_command)
            )
        except ResourceError as e:
            raise ConnectError from e
        else:
            if not resource:
                raise ConnectError(
                    "Failed to connect to instrument."
                )  # FIXME Why is this code unreachable?

            self.instrument = resource
            self.instrument_type = SerialInstrument
            if self.serial_instrument_baudrate:
                self.instrument.baud_rate = self.serial_instrument_baudrate

    def get_name(self) -> str:
        """Get device identification.

        :return: Device Name
        """
        return self._query("*IDN?")

    def identify(self) -> InstrumentIdentificationInfo:
        """Instrument identification."""
        instrument_id: str = self.get_name()
        instrument_id_split = instrument_id.split(",")
        self.identification = InstrumentIdentificationInfo(
            manufacturer=instrument_id_split[0],
            model=instrument_id_split[1],
            serial_number=instrument_id_split[2],
            firmware=instrument_id_split[3].strip("\n"),
        )
        return self.identification

    def reset(self) -> None:
        """Reset instrument."""
        self._write("*RST")

    def toggle_instrument_status_checking(self, status_check_state: bool = True) -> None:
        """Toggles instrument status checking for RsInstruments only.

        :param status_check_state: State of status_check flag. Defaults to True.
        :raises ValueError: When instrument_type is not RsInstrument.
        """
        if not isinstance(self.instrument, RsInstrument):
            raise ValueError(
                "Incorrect Instrument type. Status checking is not available for this instrument."
            )

        self.instrument.instrument_status_checking = status_check_state

    def _write(self, command: str) -> None:
        """Writes command to instrument.

        :param command: Command to send to instrument.
        :raises InstrumentError: When there is no connected device.
        :raises InstrumentError: When writing to GPIB instrument fails.
        :raises InstrumentError: When writing to RsInstrument fails.
        """
        if not self.instrument:
            raise InstrumentError("No connected device.")

        if isinstance(self.instrument, RsInstrument):
            try:
                self.instrument.write(command)
            except StatusException as e:
                raise InstrumentError from e
        else:
            should_retry = True
            retry_count = 10
            num_retries = 0
            while should_retry and num_retries < retry_count:
                try:
                    bytes_written: int = self.instrument.write(command)
                    if bytes_written == 0:
                        raise InstrumentError("Zero bytes were written to device.")
                except (ConnectionResetError, pyvisa.errors.VisaIOError):
                    self.instrument.close()
                    self.connect()
                    num_retries += 1
                else:
                    should_retry = False

    def _query(self, command: str) -> str:
        """Queries command to instrument and returns the response.

        :param command: Command to send to instrument.
        :raises InstrumentError: When there is no connected device.
        :raises InstrumentError: When querying to GPIB instrument fails.
        :raises InstrumentError: When querying to RsInstrument fails.
        :return: Output of query.
        """
        if not self.instrument:
            raise InstrumentError("No connected device.")

        if isinstance(self.instrument, RsInstrument):
            try:
                query_result: str = self.instrument.query(command)
            except StatusException as e:
                raise InstrumentError from e
        else:
            should_retry = True
            retry_count = 10
            num_retries = 0
            while should_retry and num_retries < retry_count:
                try:
                    query_result = self.instrument.query(command)
                    if not query_result:
                        raise InstrumentError(f"Query failed: {command}")
                except (ConnectionResetError, pyvisa.errors.VisaIOError):
                    self.instrument.close()
                    self.connect()
                    num_retries += 1
                else:
                    should_retry = False

        return query_result

    def _read(self) -> str:
        """Reads output from instrument and returns it.

        :param command: Command to send to instrument.
        :raises InstrumentError: When there is no connected device.
        :raises ValueError: When the instrument type does not support read.
        :return: Output of read.

        """
        if not self.instrument:
            raise InstrumentError("No connected device.")
        elif not (
            isinstance(self.instrument, GPIBInstrument)
            or isinstance(self.instrument, TCPIPInstrument)
            or isinstance(self.instrument, TCPIPSocket)
            or isinstance(self.instrument, USBInstrument)
        ):
            raise ValueError("Read is not supported on this instrument.")
        else:
            should_retry = True
            retry_count = 10
            num_retries = 0
            while should_retry and num_retries < retry_count:
                try:
                    value = self.instrument.read()
                except (ConnectionResetError, pyvisa.errors.VisaIOError):
                    self.instrument.close()
                    self.connect()
                    num_retries += 1
                else:
                    should_retry = False

            return value

    def close(self) -> None:
        """Disconnects instrument.

        :raises InstrumentError: If there is no connected device.
        """
        if self.instrument:
            self.instrument.close()
            self.instrument = None
            self.connected = False

    def set_timeout(self, timeout: float) -> None:
        """Sets timeout value of instrument.

        :param timeout: timeout in ms for all I/O operations
        """
        if isinstance(self.instrument, RsInstrument):
            self.instrument.visa_timeout = timeout
        else:
            self.instrument.timeout = timeout

    def get_timeout(self) -> float:
        """Gets timeout value of instrument.

        :return: Timeout value of resource as float.
        """
        if isinstance(self.instrument, RsInstrument):
            timeout: float = self.instrument.visa_timeout
        else:
            timeout = self.instrument.timeout

        return timeout

    def __enter__(self):
        """Connect to instrument in context manager."""
        return self.connect()

    def __exit__(self, type_, value, traceback):  # noqa: ANN001
        """Close connection to instrument in context manager."""
        return self.close()
