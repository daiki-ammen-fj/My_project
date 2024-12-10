"""Selection state class."""


class SelectionState:
    """Utility class to represent on ON/OFF state."""

    ON = "ON"
    OFF = "OFF"

    def __init__(self, on: bool = True):
        """Constructor.

        :param on: Whether the state is on.
        """
        self._state = self.ON if on else self.OFF

    def get_state(self) -> str:
        """Getter for state value.

        :return: str of state 'ON' or 'OFF'
        """
        return self._state
