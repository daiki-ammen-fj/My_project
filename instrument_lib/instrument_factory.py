"""Instrument Factory."""

from instrument_lib import SCPIInstrument  # Your base class
from typing import Type

__all__ = ["make_scpi_instrument"]


def make_scpi_instrument(connection_string: str) -> SCPIInstrument:
    """Creates an instrument driver based on its identification.

    This factory method connects to the instrument using the provided connection
    string, retrieves its identification, and returns an instance of the appropriate
    driver class.

    Args:
        connection_string (str): The connection string used to connect to the instrument.

    Returns:
        SCPIInstrument: An instance of the appropriate instrument driver class.

    Raises:
        ValueError: If the instrument model is not recognized or unsupported.
    """
    # Use the base class to establish the connection and retrieve the IDN information
    temp_instrument = SCPIInstrument(
        ip_address=connection_string
    )  # Adjust as per your connection logic
    temp_instrument.connect()

    # Retrieve the instrument identification
    instrument_model = temp_instrument.identification.model
    temp_instrument.close()

    # Find the driver class that supports this model by checking all subclasses of SCPIInstrument
    driver_class: Type[SCPIInstrument]
    for cls in SCPIInstrument.__subclasses__():
        if hasattr(cls, "ACCEPTED_MODELS") and instrument_model in cls.ACCEPTED_MODELS:
            driver_class = cls
            break

    if not driver_class:
        raise ValueError(f"Instrument model '{instrument_model}' not recognized.")

    # Instantiate the appropriate driver with the same connection settings
    instrument_driver = driver_class(
        gpib=temp_instrument.gpib,
        ip_address=temp_instrument.ip_address,
        usb=temp_instrument.usb,
    )

    return instrument_driver
