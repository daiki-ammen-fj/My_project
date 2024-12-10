"""Input selection class."""


class InputSelection:
    """Utility class to represent different input states."""

    INPUTS = {1: "INPUT1", 2: "INPUT2"}

    def __init__(self, input_number: int):
        """Constructor.

        :param input_number: Integer for input number.
        """
        if input_number > 0:
            input_ = self.INPUTS.get(input_number, None)
            if input_:
                self._input = input_
            else:
                raise ValueError("Bad value supplied as input number.")

    def get_input(self) -> str:
        """Getter for input value.

        :return: str of input
        """
        return self._input
