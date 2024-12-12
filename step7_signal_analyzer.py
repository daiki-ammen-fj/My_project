#!python3.11
# step7_signal_analyzer.py

import time
from logging import getLogger, INFO, StreamHandler
from instrument_lib import RS_FSx  # Import the instrument driver
import socket

def connect_signal_analyzer(ip_address: str, password: str, FSWP: bool = False) -> None:
    """Connects to the Signal Analyzer and verifies the connection."""
    
    # Setup logger for displaying information
    logger = getLogger()
    logger.setLevel(INFO)
    logger.addHandler(StreamHandler())

    try:
        # Connect to the RS_FSx Spectrum Analyzer
        logger.info(f"Connecting to RS_SMx Spectrum Analyzer at IP: {ip_address}...")
        sa = RS_FSx(ip_address=ip_address)

        # Connect to the device with a timeout of 10 seconds
        sa.connect(timeout=10)
        logger.info(f"Connected. Device info: {sa.identification}")

        # Get and display the device name
        id_ = sa.get_name()
        logger.info(f"Device Name: {id_}")

        # If needed, you can check the frequency here
        # freq = sa.get_freq()
        # logger.info(f"Frequency: {freq} Hz")

        # Successfully connected, no further actions
        logger.info("Connection successful, exiting step7.")

        # Close connection
        sa.close()

    except (socket.timeout, ConnectionError) as e:
        logger.error(f"Connection failed: {e}")
    except Exception as e:
        logger.error(f"An unexpected error occurred: {e}")
