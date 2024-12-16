#!python3.11
# main.py

import logging
import sys,argparse
from time import sleep
from step1_connect import connect_to_cato_client, connect_through_jump_server
from step2_run_batch import run_batch_script
from step3_ngp800 import control_ngp800
from step4_run_paam import run_paam_script
from step5_psg import configure_keysight_psg
from step6_smw200a import configure_r_and_s_smw200a
from step7_spectrum_analyzer import connect_spectrum_analyzer
from measurement_module.measurement import perform_measurements, initialize_instruments

# argparser
parser = argparse.ArgumentParser(description='debug arguments')    #argument for debug description

# add args
parser.add_argument('-b','--batch', help='この引数の説明（なくてもよい）', default=r"C:\Users\labuser\qlight-control\run_qlight_check.bat")    #Must args
parser.add_argument('-p','--paam' , help='この引数の説明（なくてもよい）', default=r"C:\Users\labuser\pybeacon\run_paam_dl_reg.bat")    #Must args

# parse args
args = parser.parse_args()

# Logging configuration
logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")

# Device credentials
DEVICE_CREDENTIALS = {
    "cato_client": {"ip": "172.22.0.12", "username": "labuser", "password": "1234"},
    "RS_ngp800": {"ip": "172.22.2.12", "username": "Instrument", "password": "instrument"},
    "RS_spectrum_analyzer": {"ip": "172.22.0.70", "username": "Instrument", "password": "894129"},
    "keysight_psg": {"ip": "172.22.2.31", "username": "Instrument", "password": "instrument"},
    "RS_signal_generator_smw200a": {"ip": "172.22.2.23", "username": "Instrument", "password": "instrument"},
    "jump_server_ip": "10.18.177.82",
}

# Flag to track the initialization state
initialized = False

def initialize(location, mode):
    """Initialization process (Step 1-7)"""
    global initialized
    try:
        if location == "2":  # Japan - Connect through Jump Server
            logging.info("Japan location selected")
            jump_username = input("Please enter your jump server username: ").strip()
            logging.info("Connecting through jump server")
            connect_through_jump_server(
                DEVICE_CREDENTIALS["jump_server_ip"],
                jump_username,
                DEVICE_CREDENTIALS["cato_client"]["ip"],
                DEVICE_CREDENTIALS["cato_client"]["username"]
            )
        elif location == "1":  # US - Connect directly to Cato client
            logging.info("US location selected")
            logging.info("Connecting directly to Cato client")
            connect_to_cato_client(
                DEVICE_CREDENTIALS["cato_client"]["ip"],
                DEVICE_CREDENTIALS["cato_client"]["username"],
            )

        logging.info("Step 2: Run the batch script")
        run_batch_script(args.batch)

        logging.info("Step 3: Control the NGP800 power supply")
        control_ngp800(DEVICE_CREDENTIALS["RS_ngp800"]["ip"])

        logging.info("Step 4: Run the PAAM download script")
        sleep(10)
        run_paam_script(args.paam)

        logging.info("Step 5: Configure Keysight PSG")
        configure_keysight_psg(DEVICE_CREDENTIALS["keysight_psg"]["ip"])

        logging.info("Step 6: Configure R&S SMW200A")
        configure_r_and_s_smw200a(
            DEVICE_CREDENTIALS["RS_signal_generator_smw200a"]["ip"],
        )

        logging.info("Step 7: Connect to the signal analyzer")
        connect_spectrum_analyzer(
            DEVICE_CREDENTIALS["RS_spectrum_analyzer"]["ip"],
        )

        initialized = True
        logging.info("Initialization completed.")
    except Exception as e:
        logging.error(f"Initialization failed: {e}", exc_info=True)
        sys.exit(1)

def get_location():
    """Prompt for location selection with validation."""
    while True:
        location = input("Please select your location: (1) US, (2) Japan: ").strip()
        if location in ["1", "2"]:
            return location
        logging.warning("Invalid location selected, please choose '1' for US or '2' for Japan.")

def get_mode():
    """Prompt for mode selection with validation."""
    while True:
        mode = input("Please select the mode: (1) Initialization Mode, (2) Measurement Mode: ").strip()
        if mode in ["1", "2"]:
            return mode
        logging.warning("Invalid mode selected, please choose '1' for Initialization Mode or '2' for Measurement Mode.")

def main():
    global initialized
    try:
        location = get_location()
        mode = get_mode()

        if mode == "1":
            logging.info("Initialization mode selected")
            initialize(location, mode)

        elif mode == "2":
            if not initialized:
                logging.warning("Initialization not performed, initializing now")
                initialize(location, mode)

            logging.info("Initializing instruments for measurement")
            rs_sm_url = DEVICE_CREDENTIALS["RS_signal_generator_smw200a"]["ip"]
            rs_fsx_url = DEVICE_CREDENTIALS["RS_spectrum_analyzer"]["ip"]
            rs_sm, rs_fsx = initialize_instruments(rs_sm_url, rs_fsx_url)

            logging.info("Measurement mode selected")

            while True:
                try:
                    perform_measurements(rs_sm, rs_fsx)
                except Exception as e:
                    logging.error(f"Measurement failed: {e}", exc_info=True)
                    break

                repeat = input("Do you want to perform the measurement again? (yes/no): ").strip().lower()
                if repeat != "yes":
                    break
        else:
            logging.warning("Invalid mode selected")
            sys.exit(1)

    except Exception as e:
        logging.error(f"Error in main process: {e}", exc_info=True)
        sys.exit(1)

if __name__ == "__main__":
    try:
        main()
    except Exception as e:
        logging.error(f"Unexpected error: {e}", exc_info=True)
        sys.exit(1)
