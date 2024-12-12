#!python3.11
# step5_psg.py

import logging
from instrument_lib import KS_PSG

# Set up logging
logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")

def configure_keysight_psg(ip):
    logging.info("Step 5: Initializing the Keysight PSG signal generator...")
    sig_gen = KS_PSG(ip_address=ip)
    try:
        sig_gen.connect()
        logging.info(f"Connected successfully! Device info: {sig_gen.identification}")

        target_frequency = 122.8e6  # 122.8 MHz
        logging.info(f"Setting the frequency to {target_frequency / 1e6:.1f} MHz...")
        sig_gen.set_freq(target_frequency)
        measured_frequency = sig_gen.get_freq()
        logging.info(f"Frequency set to: {measured_frequency / 1e6:.1f} MHz.")

        target_amplitude = -20  # -20 dBm
        logging.info(f"Setting the amplitude to {target_amplitude} dBm...")
        sig_gen.set_amplitude(target_amplitude)
        measured_amplitude = sig_gen.get_amplitude()
        logging.info(f"Amplitude set to: {measured_amplitude} dBm.")

        logging.info("Keysight PSG control command executed successfully.")
    except Exception as e:
        logging.error(f"Failed to configure Keysight PSG: {e}")
        raise  # Re-raise the exception to propagate the error
