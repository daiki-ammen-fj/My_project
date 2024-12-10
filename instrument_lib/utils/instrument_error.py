"""Instrument Exception class."""


class InstrumentError(Exception):
    """Utility class for exceptions in this module."""


class ConnectError(InstrumentError):
    """Exception when connecting to instrument hardware."""


class PositionerError(InstrumentError):
    """Exception relating to positioner."""
