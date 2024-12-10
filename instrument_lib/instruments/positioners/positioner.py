"""Abstract base class for positioner."""

from typing import Protocol

from instrument_lib.instruments.instrument import Instrument


class Positioner(Instrument, Protocol):
    """Abstract base class for power supply.

    Args:
        Protocol: Python typing Protocol object
    """

    def connect(self) -> None:
        """Deriving classes should implement connect."""

    def close(self) -> None:
        """Deriving classes should implement close."""

    def move_to_theta_phi(self, theta: float, phi: float) -> None:
        """Move the positioner to a certain angle defined in Theta-Phi coordinate system."""

    def move_to_azimuth_elevation(self, azimuth: float, elevation: float) -> None:
        """Move the positioner to a certain angle defined in Azimuth-Elevation coordinate system."""

    def move_to_degrees(self, id_: int, angle: float) -> None:
        """For compatibility with the other positioner."""

    def get_current_position(self) -> tuple[float, float]:
        """Return the current position in Theta-Phi coordinate system."""

    def get_positioner_id(self) -> str:
        """Queries the ID of the device. Returns string identifying the device.

        Can include company, positioner type, or IP address.
        """

    def seek_position(self, axis: str, angle: float) -> None:
        """Instructs the device to begin seeking for a specified target position.

        Args:
            axis: 'Theta' or 'Phi'
            angle: Angle in degrees to seek.
        """


def is_positioner_type(_: Positioner) -> None:
    """Empty method to type check if type is a Positioner."""
    ...
