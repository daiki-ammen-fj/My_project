"""GPIO Pin module."""

from dataclasses import dataclass


@dataclass(eq=True, frozen=True)
class GPIOPin:
    """Class for GPIO Pin."""

    pin: int | tuple[int, int]
