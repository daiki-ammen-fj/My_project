"""Qlight module."""

from enum import Enum
import socket
import time
from typing import List, Optional

from instrument_lib.instruments.instrument import Instrument

IP_PORT: int = 20000


class RW(Enum):
    """Enums for Read/Write."""

    WRITE = 0x57
    READ = 0x52


class LightType(Enum):
    """Enum for light type."""

    WS = 0x00
    WP = 0x01
    WM = 0x02
    WA = 0x03
    WB = 0x04


class LightState(Enum):
    """Enum for light state."""

    OFF = 0x00
    ON = 0x01
    BLINK = 0x02
    NONE = 0x64


class Color(Enum):
    """Enum for color."""

    RED = 2
    ORANGE = 3
    GREEN = 4
    BLUE = 5
    WHITE = 6


class Qlight(Instrument):
    """Qlight class."""

    def __init__(self, ip_addr: str, sleep_time: float = 0.1) -> None:
        """Constructor.

        :param ip_addr: IP address of Qlight
        """
        self.ip_addr: str = ip_addr
        self.sleep_time: float = sleep_time

    def connect(self) -> None:
        """Connect to Qlight."""
        self.s: Optional[socket.socket] = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.s.connect((self.ip_addr, IP_PORT))
        self.connected = True

        time.sleep(2)

    def close(self) -> None:
        """Disconnect from Qlight."""
        if isinstance(self.s, socket.socket):
            self.s.close()
        self.s = None
        self.connected = False

    def change_color(
        self, color: Color, state: LightState, type_: LightType = LightType.WS
    ) -> None:
        """Change Qlight color.

        :param color: Color to change Qlight to.
        :param state: What state should that light be in.
        :param type_: Light type.
        """
        new_val_: List[int] = [RW.WRITE.value, type_.value]

        for i in range(2, 8):
            if i != color.value:
                new_val_.append(LightState.NONE.value)
            else:
                new_val_.append(state.value)

        if self.s:
            self.s.send(bytearray(new_val_))
        time.sleep(self.sleep_time)

    def all_on(self) -> None:
        """Turn all lights on."""
        new_val_: List[int] = [RW.WRITE.value, LightType.WS.value]

        for _ in range(2, 7):
            new_val_.append(LightState.ON.value)

        new_val_.append(LightState.NONE.value)
        if self.s:
            self.s.send(bytearray(new_val_))
        time.sleep(self.sleep_time)

    def all_off(self) -> None:
        """Turn all lights off."""
        new_val_: List[int] = [RW.WRITE.value, LightType.WS.value]

        for _ in range(2, 7):
            new_val_.append(LightState.OFF.value)

        new_val_.append(LightState.NONE.value)
        if self.s:
            self.s.send(bytearray(new_val_))
        time.sleep(self.sleep_time)
