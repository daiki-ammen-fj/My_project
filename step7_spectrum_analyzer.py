#!python3.11 
# step7_spectrum_analyzer.py

from logging import getLogger, INFO, StreamHandler, Formatter  # Add Formatter import
from instrument_lib import RS_FSx  # Import the instrument driver
import socket

def connect_spectrum_analyzer(ip):
    """Connects to the Signal Analyzer and verifies the connection."""
    
    # Setup logger for displaying information
    logger = getLogger()
    logger.setLevel(INFO)
    
    # Setup StreamHandler for logging to the console
    handler = StreamHandler()
    
    # Setting up the log format (Timestamp, log level, and message)
    formatter = Formatter('%(asctime)s - %(levelname)s - %(message)s')  # Use Formatter object
    handler.setFormatter(formatter)
    
    # Add the handler to the logger
    logger.addHandler(handler)

    try:
        logger.info(f"Connecting to RS_SMx Spectrum Analyzer at IP address: {ip}...")
        
        # Create the RS_FSx object and try to connect
        sa = RS_FSx(ip_address=ip)
        logger.info("RS_FSx object created successfully.")
        
        logger.info("Attempting to connect to the device...")
        sa.connect()  # Assuming the method doesn't support a timeout argument
        logger.info(f"Connected. Device info: {sa.identification}")

        # Get and display the device name
        id_ = sa.get_name()
        logger.info(f"Device Name: {id_}")

        # Successfully connected, no further actions
        logger.info("Connection successful, exiting.")

        # Close connection
        sa.close()

    except (socket.timeout, ConnectionError) as e:
        logger.error(f"Connection failed: {repr(e)}")  # Changed to repr for better visibility of error details
    except Exception as e:
        logger.error(f"An unexpected error occurred: {repr(e)}")  # Changed to repr for better visibility of error details

if __name__ == "__main__":
    # Directly specify the IP address
    ip_address = "172.22.0.70"  # Replace with the desired IP address

    connect_spectrum_analyzer(ip_address)
