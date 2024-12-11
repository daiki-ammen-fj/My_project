# step6_smw200a.py

import logging
from instrument_lib import RS_SMx  # Import the instrument driver

# Set up logging
logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")

def configure_r_and_s_smw200a(url: str, password: str) -> None:
    """Configures the R&S SMW200A signal generator."""
    logging.info("Step 6: Initializing R&S SMW200A Signal Generator...")

    # Create an instance of the RS_SMx driver
    sig_gen = RS_SMx(ip_address=url)  # Use the URL as the IP address

    try:
        # Connect to the signal generator
        logging.info("Connecting to R&S SMW200A Signal Generator...")
        sig_gen.connect()
        logging.info(f"Connected successfully! Device info: {sig_gen.identification}")

        # Set and verify frequency
        target_frequency = 5.16144e9  # 5.16144 GHz
        logging.info(f"Setting frequency to {target_frequency / 1e9:.5f} GHz...")
        sig_gen.set_freq(target_frequency)
        current_frequency = sig_gen.get_freq()
        logging.info(f"Current Frequency: {current_frequency / 1e9:.5f} GHz")
        assert current_frequency == target_frequency, "Frequency mismatch!"

        # Set and verify power level
        target_power_level = -40  # -40 dBm
        logging.info(f"Setting power level to {target_power_level} dBm...")
        sig_gen.set_power_level(target_power_level)
        current_power_level = sig_gen.get_power()
        logging.info(f"Current Power Level: {current_power_level} dBm")
        assert current_power_level == target_power_level, "Power level mismatch!"

        logging.info("Step 6 complete. R&S SMW200A is configured successfully.")

    except Exception as e:
        logging.error(f"Failed to configure R&S SMW200A: {e}")
        raise  # Re-raise the exception to propagate the error
