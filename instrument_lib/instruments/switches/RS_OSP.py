"""Driver for OSP Switch."""

import json
import os
from typing import Optional
import time

import instrument_lib
from instrument_lib.utils import GPIBNumber
from instrument_lib.instruments.instrument import SCPIInstrument


class RS_OSP(SCPIInstrument):
    """OSP Switcher.

    This instrument controls a set of switches that connect instruments
    and DUT/Antennas in a physical test environment.
    """

    ACCEPTED_MODELS = [
        "OSP320",
    ]

    def __init__(
        self,
        gpib: GPIBNumber | None = None,
        ip_address: str | None = None,
        usb: tuple[str, str, str] | None = None,
        wireless: bool = False,
        simulate: bool = False,
        retry: int = 10,
        config: str = "configs/template_config.json",
    ):
        """Constructor.

        :param ip_address: IP Address as a string.
        :param retry: Number of times to retry certain commands.
        """
        super().__init__(gpib, ip_address, usb, wireless, simulate)
        self.retry: int = retry
        self.rsinstrument = True
        lib_path = instrument_lib.__path__[0]
        with open(os.path.join(lib_path, config), "r") as f:
            self.config = json.load(f)["Switch"]

    def connect(self) -> None:
        """Connects to RS OSP Switch.

        If connection attempt fails
        method retrys establishing connection the amount specified by
        instance variable retry.

        Raises:
            ConnectionError: If connection cannot be established.
        """
        if self.retry == 0:
            try:
                super().connect()
                return
            except Exception as e:
                raise ConnectionError("Could not establish connection to OSP Switch.") from e

        retry_attempts: int = 0
        while retry_attempts < self.retry:
            try:
                super().connect()
                return
            except Exception as e:
                if retry_attempts == self.retry - 1:
                    raise ConnectionError(
                        f"Could not establish connection after {self.retry} attempts."
                    ) from e
                else:
                    retry_attempts += 1
                    time.sleep(0.1)

    def write(self, frame: str, module: str, switch_val: str, switch_name: str) -> None:
        """Wrapper for write method. Writes switch_val to switch_name on module and frame.

        Example usage:
        ROUTe:CLOSe (@F01M060111)
        :param frame: Frame number. Ex) F01.
        :param module: Module number. Ex) M06, M07, M08
        :param switch_val: New switch state.
                           00=OFF,01=ON for binary switches, 01,..,06 for 6-1 switches
        :param switch_name: Name of switch.
                            K11 = 11,...,16=K16 for binary switches, K1-1=01, K1-2=01
        """
        self._write(command=f"ROUTe:CLOSe (@{frame}{module}({switch_val}{switch_name}))")

    def write_path_str(self, path_str: str) -> None:
        """Writes entire path string to OSP."""
        self._write(command=f"ROUTe:CLOSe {path_str}")

    def load_switch_network(self, switch_network: str) -> None:
        """Load switch network data for a particular network.

        :param switch network: Mapping of switch data.
        """
        self.switch_network: dict = self.config[switch_network]
        self.paths: dict[str, str] = self.switch_network["paths"]

    def connect_instrument_setup(self, instrument_setup: str) -> None:
        """Connects instruments to sources.

        :param instrument_setup: Name of instrument setup (ex Three-Instrument-RX-V)
        """
        instrument_connections: list[str] = self.switch_network[instrument_setup]
        for instrument_connection in instrument_connections:
            path_str: str = self.paths[instrument_connection]
            self.write_path_str(path_str)
