#!python3.11
# step3_ngp800.py

import logging
from instrument_lib import RS_NGPx
from time import sleep

# Set up logging
logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")

def control_ngp800(ip):
    logging.info("Step 3: Connecting to NGP800 Power Supply...")
    power_supply = RS_NGPx(ip_address=ip)
    try:
        # Attempt to connect to the power supply
        power_supply.connect()
        logging.info(f"Connected successfully! Device info: {power_supply.identification}")

        target_current = 2.0  # 2 Amperes
        logging.info(f"Setting current to {target_current} A on channel 1...")
        power_supply.set_current(1, target_current)
        sleep(1)  # Wait for 1 second
        current = power_supply.get_current(1)
        logging.info(f"Measured Current on Channel 1: {current} A")

        # Check if the measured current matches the target current
        if current != target_current:
            logging.error(f"Current mismatch! Expected: {target_current} A, but got: {current} A")
            raise ValueError(f"Current mismatch: Expected {target_current} A, but got {current} A")

        target_voltage = 1.1  # 1.1 Volts
        logging.info(f"Setting voltage to {target_voltage} V on channel 1...")
        power_supply.set_voltage(1, target_voltage)
        sleep(1)  # Wait for 1 second
        voltage = power_supply.get_voltage(1)
        logging.info(f"Measured Voltage on Channel 1: {voltage} V")

        # Check if the measured voltage matches the target voltage
        if voltage != target_voltage:
            logging.error(f"Voltage mismatch! Expected: {target_voltage} V, but got: {voltage} V")
            raise ValueError(f"Voltage mismatch: Expected {target_voltage} V, but got {voltage} V")

        logging.info("Turning ON power for Channel 1...")
        power_supply.toggle_channel_output_state(1, 1)

        logging.info("NGP800 control command executed successfully.")
    except Exception as e:
        logging.error(f"Failed to control NGP800: {e}")
        raise  # Re-raise the exception to propagate the error

