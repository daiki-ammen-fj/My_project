"""Generic RF Switch module."""

import platform
from typing import Protocol

from instrument_lib.utils.gpio_pin import GPIOPin
from instrument_lib.instruments.instrument import Instrument


class Switch(Instrument, Protocol):
    """Generic Switch protocol."""

    def connect(self) -> None:
        """Deriving classes should implement connect."""
        ...

    def close(self) -> None:
        """Deriving classes should implement close."""
        ...

    def set(self, pin: GPIOPin) -> None:
        """Set GPIO pin to logic high."""
        ...

    def clear(self, pin: GPIOPin) -> None:
        """Clear GPIO pin to logic low."""
        ...


def make_switch() -> Switch:
    """Switch factory class."""

    platform_str = platform.platform()

    if "Windows" in platform_str:
        from instrument_lib.instruments.switches.NI6501 import NISwitch

        return NISwitch()
    elif "rpi" in platform_str:
        from instrument_lib.instruments.switches.rpi_switch import RPISwitch

        return RPISwitch()
    else:
        raise OSError(f"Invalid operating system for RF Switch {platform_str}")


class RFSwitch:
    """Generic RF Switch class interface."""

    def __init__(self) -> None:
        """Constructor."""

        self.switch = make_switch()

    def connect(self) -> None:
        """Connect to switch instrument."""
        self.switch.connect()

    def close(self) -> None:
        """Close connection to switch instrument."""
        self.switch.close()

    def set(self, pin: GPIOPin) -> None:
        """Set GPIO pin to logic high."""
        self.switch.set(pin)

    def clear(self, pin: GPIOPin) -> None:
        """Clear GPIO pin to logic low."""
        self.switch.clear(pin)
