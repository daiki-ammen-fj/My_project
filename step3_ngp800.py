#!python3.11
# step3_ngp800.py
import os 
from instrument_lib import RS_NGPx
from time import sleep
import logging
import time

# Operate the NGP800 using SCPI commands, without using VNC.
# Function to control the NGP800 power supply using SCPI commands
def control_ngp800(ip):
    print("Step 3: Connecting to NGP800 Power Supply...")
    try:
        # Connect to the NGP800 power supply
        power_supply = RS_NGPx(ip_address=ip)
        power_supply.connect()
        print(f"Connected successfully! Device info: {power_supply.identification}")

        # Set the current to 2.0A on channel 1
        target_current = 2.0
        power_supply.set_current(1, target_current)
        sleep(1)
        current = power_supply.get_current(1)
        assert current == target_current, "Current mismatch!"  # Ensure the set current is correct

        # Set the voltage to 1.1V on channel 1
        target_voltage = 1.1
        power_supply.set_voltage(1, target_voltage)
        sleep(1)
        voltage = power_supply.get_voltage(1)
        assert voltage == target_voltage, "Voltage mismatch!"  # Ensure the set voltage is correct

        # Turn on the output on channel 1
        power_supply.toggle_channel_output_state(1, 1)
        print("NGP800 control command executed successfully.")
    except Exception as e:
        print(f"Failed to control NGP800: {e}")
        raise

# Main execution of the script
if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")

    try:
        # Get the NGP800 IP from environment variable or use default
        ngp_ip = os.getenv('NGP_IP', '172.22.2.12')
        control_ngp800(ip=ngp_ip)  # Control the NGP800 with the provided IP
    except Exception as e:
        logging.error(f"Error in Step 3 process: {e}")
        raise
