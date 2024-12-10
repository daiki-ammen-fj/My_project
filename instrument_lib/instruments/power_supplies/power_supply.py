"""Abstract base class for power supply."""

from typing import Protocol

from instrument_lib.instruments.instrument import Instrument


class PowerSupply(Instrument, Protocol):
    """Abstract base class for power supply.

    Args:
        Protocol: Python typing Protocol object
    """

    def connect(self) -> None:
        """Deriving classes should implement connect."""

    def close(self) -> None:
        """Deriving classes should implement close."""

    def on(self, channel: str = "ALL") -> None:
        """Turn on power supply."""

    def off(self, channel: str = "ALL") -> None:
        """Turn off power supply."""

    def set_voltage(self, voltage: float, channel: int) -> None:
        """Set power supply voltage."""

    def get_voltage(self, channel: int) -> float:
        """Get power supply voltage."""

    def set_current(self, channel: int, current: float) -> None:
        """Set power supply current."""

    def get_current(self, channel: int) -> float:
        """Read current draw from PS.

        Args:
            channel: Channel to read from.

        Returns:
            Current draw in Amps.
        """


def is_power_supply_type(_: PowerSupply) -> None:
    """Empty method to type check if type is a PowerSupply."""
    ...
