#!python3.11
# step5_psg.py

import logging
from time import sleep  # Import sleep to wait for 1 second
from instrument_lib import KS_PSG

# Logging configuration
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s"
)

def configure_keysight_psg(ip, debug_mode=False):
    """
    Configure the Keysight PSG signal generator with specified settings.

    Args:
        ip (str): IP address of the Keysight PSG signal generator.
        debug_mode (bool): If True, enables debug messages but skips actual configuration.
    """
    logging.info("Step 5: Initializing the Keysight PSG signal generator...")
    sig_gen = KS_PSG(ip_address=ip)  # Connect to the signal generator using the provided IP address

    try:
        # Connect to the signal generator
        sig_gen.connect()
        logging.info(f"Connected successfully! Device info: {sig_gen.identification}")

        # Set the frequency to 122.8 MHz
        target_frequency = 122.8e6  # 122.8 MHz
        if not debug_mode:
            logging.info(f"Setting the frequency to {target_frequency / 1e6:.1f} MHz...")
            sig_gen.set_freq(target_frequency)
            measured_frequency = sig_gen.get_freq()
            logging.info(f"Frequency set to: {measured_frequency / 1e6:.1f} MHz.")
        else:
            logging.info(f"Debug mode: Skipping frequency configuration (target: {target_frequency / 1e6:.1f} MHz).")

        # Set the amplitude to -20 dBm
        target_amplitude = -20  # -20 dBm
        if not debug_mode:
            logging.info(f"Setting the amplitude to {target_amplitude} dBm...")
            sig_gen.set_amplitude(target_amplitude)
            measured_amplitude = sig_gen.get_amplitude()
            logging.info(f"Amplitude set to: {measured_amplitude} dBm.")
        else:
            logging.info(f"Debug mode: Skipping amplitude configuration (target: {target_amplitude} dBm).")

        # Enable the RF output
        if not debug_mode:
            logging.info("Enabling the RF output...")
            sig_gen.rf_switch('ON')  # Turn on the RF output
            logging.info("RF output enabled successfully.")
        else:
            logging.info("Debug mode: Skipping RF output enable command.")

        # Wait for 1 second
        sleep(1)

        # Get the current power output (always retrieve this value)
        current_power = sig_gen.get_power()  # Get the current power in dBm
        logging.info(f"Current output power: {current_power} dBm.")

        logging.info("Keysight PSG control command executed successfully.")
    
    except Exception as e:
        logging.error(f"Failed to configure Keysight PSG: {e}", exc_info=True)
        raise

# Main execution
if __name__ == "__main__":
    ip = "172.22.2.31"  # Replace this with the desired IP address
    debug_mode = False  # Change to True to enable debug mode

    try:
        configure_keysight_psg(ip, debug_mode)
    except Exception as e:
        logging.error(f"Error during Keysight PSG configuration: {e}")
