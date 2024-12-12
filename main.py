#!python3.11
#!python3.11
# main.py

import logging
import sys
from time import sleep
from step1_connect import connect_to_cato_client
from step2_run_batch import run_batch_script
from step3_ngp800 import control_ngp800
from step4_run_paam import run_paam_script
from step5_psg import configure_keysight_psg
from step6_smw200a import configure_r_and_s_smw200a
from step7_signal_analyzer import connect_signal_analyzer
from measurement_module.measurement import perform_measurements, initialize_instruments  # Measurement processing module

# Logging configuration
logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")

# Device credentials
DEVICE_CREDENTIALS = {
    "cato_client": {"ip": "172.22.0.12", "username": "admin", "password": "1234"}, 
    "tightvnc_ngp800": {"ip": "172.22.2.12"}, # NGP800 Power supply IP
    "tightvnc_signal_analyzer": {"ip": "172.22.0.70", "password": "894129"}, # RS_SMx IP
    "keysight_psg": {"ip": "172.22.2.31"}, # Keysight E8257D PSG IP
    "r_and_s_smw200a": {"url": "http://172.22.2.23", "password": "instrument"} # RS FSx IP
}

# Flag to track the initialization state
initialized = False

def initialize():
    """Initialization process (Step 1-7)"""
    global initialized
    try:
        logging.info("Step 1: Connect to Cato client")
        connect_to_cato_client(DEVICE_CREDENTIALS["cato_client"]["ip"], DEVICE_CREDENTIALS["cato_client"]["password"])

        logging.info("Step 2: Run the batch script")
        run_batch_script(r"C:\Users\labuser\qlight-control\run_qlight_check.bat")

        logging.info("Step 3: Control the NGP800 power supply")
        control_ngp800(DEVICE_CREDENTIALS["tightvnc_ngp800"]["ip"])

        logging.info("Step 4: Run the PAAM download script")
        sleep(10)
        run_paam_script(r"C:\Users\labuser\pybeacon\run_paam_dl_reg.bat")

        logging.info("Step 5: Configure Keysight PSG")
        configure_keysight_psg(DEVICE_CREDENTIALS["keysight_psg"]["ip"])

        logging.info("Step 6: Configure R&S SMW200A")
        configure_r_and_s_smw200a(DEVICE_CREDENTIALS["r_and_s_smw200a"]["url"], DEVICE_CREDENTIALS["r_and_s_smw200a"]["password"])

        logging.info("Step 7: Connect to the signal analyzer")
        connect_signal_analyzer(DEVICE_CREDENTIALS["tightvnc_signal_analyzer"]["ip"], DEVICE_CREDENTIALS["tightvnc_signal_analyzer"]["password"])

        initialized = True
        logging.info("Initialization completed.")
    except Exception as e:
        logging.error(f"Initialization failed: {e}", exc_info=True)
        exit(1)

def main():
    global initialized
    # Mode selection: Initialization mode or Measurement mode
    mode = input("Please select the mode: (1) Initialization Mode, (2) Measurement Mode: ").strip()

    if mode == "1":
        logging.info("Initialization mode selected")
        initialize()
    elif mode == "2":
        if not initialized:
            logging.warning("Initialization not performed, initializing now")
            initialize()

        # Initialize instruments for measurement
        logging.info("Initializing instruments for measurement")
        rs_sm, rs_fsx = initialize_instruments()  # Initialize RS_SMx and RS_FSx

        logging.info("Measurement mode selected")
        while True:
            perform_measurements(rs_sm, rs_fsx)  # Execute the measurement process with the initialized instruments
            repeat = input("Do you want to perform the measurement again? (yes/no): ").strip().lower()
            if repeat != "yes":
                break
    else:
        logging.warning("Invalid mode selected")
        exit(1)

if __name__ == "__main__":
    main()

