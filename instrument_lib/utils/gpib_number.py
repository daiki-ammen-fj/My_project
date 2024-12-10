"""GPIB Number class."""


class GPIBNumber:
    """Utility class to represent different GPIB numbers."""

    MIN_GPIB: int = 1
    MAX_GPIB: int = 31

    def __init__(self, gpib_number: int):
        """Constructor.

        :param gpib_number: Integer for gpib number, between 1 and 31.
        """
        if self.MIN_GPIB <= gpib_number <= self.MAX_GPIB:
            self.value = gpib_number
        else:
            msg: str = (
                f"Invalid gpib_number supplied."
                f"Value must be between {self.MIN_GPIB} and {self.MAX_GPIB}"
            )
            raise ValueError(msg)

    def __str__(self) -> str:
        """String representation of GPIBNumber."""
        return str(self.value)
