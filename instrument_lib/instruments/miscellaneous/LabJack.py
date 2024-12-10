"""Driver for LabJack T7 Pro."""

import contextlib
import io
import logging

logger = logging.getLogger(__name__)


def import_silently(package_name: str) -> None:
    """Helper method to silently import labjack ljm and redirect error message to debug logger."""
    with contextlib.redirect_stdout(io.StringIO()) as f:
        __import__(package_name)

    logger.debug(f.getvalue())


import_silently("labjack.ljm")  # silence the labjack

from labjack import ljm  # type: ignore

from instrument_lib.utils import InstrumentError
from instrument_lib.instruments.instrument import Instrument


class LabJack(Instrument):
    """Driver for LabJack T7 Pro."""

    def __init__(self) -> None:
        """Constructor."""
        self.instrument: int | None = None

    def connect(self) -> None:
        """Connect to instrument.

        :raises InstrumentError: If connecting to device fails
        """
        try:
            instrument = ljm.openS("T7", "ANY", "ANY")
        except ljm.LJMError as e:
            raise InstrumentError from e
        except AttributeError as e:
            raise InstrumentError(
                "Cannot connect to labjack device because labjack.dll is missing."
            ) from e
        else:
            self.instrument = instrument

    def close(self) -> None:
        """Close connection with instrument."""
        ljm.close(self.instrument)

    def read_temperature(self, channel: int = 0) -> float:
        """Reads temperature (in degrees C) from instrument.

        :param channel: Channel number to read, defaults to 0.
        :return: temperature reading from instrumet in degrees C.
        """
        names = [
            f"AIN{channel}_EF_INDEX",
            f"AIN{channel}_EF_CONFIG_A",
            f"AIN{channel}_EF_CONFIG_B",
            f"AIN{channel}_NEGATIVE_CH",
            f"AIN{channel}_EF_CONFIG_D",
            f"AIN{channel}_EF_CONFIG_E",
        ]
        values = [24, 1, 60052, channel + 1, 1.0, 0.0]
        ljm.eWriteNames(self.instrument, len(names), names, values)

        temperature: float = ljm.eReadName(self.instrument, f"AIN{channel}_EF_READ_A")

        return temperature
