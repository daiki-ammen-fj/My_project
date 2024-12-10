"""Identification."""

from dataclasses import dataclass


@dataclass
class InstrumentIdentificationInfo:
    """Instrument Identification Data Class."""

    manufacturer: str
    model: str
    serial_number: str
    firmware: str
