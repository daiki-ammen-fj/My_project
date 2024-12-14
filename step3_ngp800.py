#!python3.11
# step3_ngp800.py

import logging
from instrument_lib import RS_NGPx
from time import sleep

# Operate the NGP800 using SCPI commands, without using VNC.
# Function to control the NGP800 power supply using SCPI commands
def control_ngp800(ip):
    logging.info("Step 3: Connecting to NGP800 Power Supply...")
    try:
        # Connect to the NGP800 power supply
        power_supply = RS_NGPx(ip_address=ip)
        power_supply.connect()
        
        # Check if the connection was successful by getting device information
        device_info = power_supply.identification
        if device_info:
            logging.info(f"Connected successfully! Device info: {device_info}")
        else:
            logging.warning("No device information received. Connection may have failed.")
            return
        
        # Enable output on channel 1
        power_supply.toggle_channel_output_state(1, 1)
        logging.info("Channel 1 output enabled.")

        # Wait for 3 seconds before checking the status
        sleep(3)

        # Get the OPP (Overload Protection) level for channel 1
        opp_level = power_supply.get_opp_level(1)
        logging.info(f"OPP level for channel 1: {opp_level}")

        # Get the upper voltage limit for channel 1
        upper_voltage_limit = power_supply.get_upper_voltage_limit(1)
        logging.info(f"Upper voltage limit for channel 1: {upper_voltage_limit}")

        # Get the upper current limit for channel 1
        upper_current_limit = power_supply.get_upper_current_limit(1)
        logging.info(f"Upper current limit for channel 1: {upper_current_limit}")

        # Get the output state for channel 1
        channel_output_state = power_supply.get_channel_output_state(1)
        logging.info(f"Channel 1 output state: {channel_output_state}")

        # Get the master output state
        master_output_state = power_supply.get_master_output_state()
        logging.info(f"Master output state: {master_output_state}")

        # Get the current safety limit state (displayed last)
        limit_state = power_supply.get_limit_state()
        logging.info(f"Current safety limit state: {limit_state}")
        
    except Exception as e:
        logging.error(f"Failed to control NGP800: {e}")
        raise

# Main execution of the script
if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")

    try:
        # Directly specify the IP address (replace with the correct one)
        ngp_ip = '172.22.2.12'  # Example IP address, replace as needed
        control_ngp800(ip=ngp_ip)  # Control the NGP800 with the provided IP
    except Exception as e:
        logging.error(f"Error in Step 3 process: {e}")
        raise
