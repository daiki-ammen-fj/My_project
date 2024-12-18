#!python3.11
# main.py

import logging
import sys, argparse
from time import sleep
from step1_connect import connect_to_SanDiego_Server, connect_through_jump_server
from step2_run_batch import run_batch_script
from step3_ngp800 import control_ngp800
from step4_run_paam import run_paam_script
from step5_psg import configure_keysight_psg
from step6_smw200a import configure_r_and_s_smw200a
from step7_spectrum_analyzer import connect_spectrum_analyzer
from measurement_module.measurement import perform_measurements, initialize_instruments

# argparser
parser = argparse.ArgumentParser(description='debug arguments')

# add args
parser.add_argument('-b','--batch', help='この引数の説明（なくてもよい）', default=r"C:\Users\labuser\qlight-control\run_qlight_check.bat")    # Must args
parser.add_argument('-p','--paam' , help='この引数の説明（なくてもよい）', default=r"C:\Users\labuser\pybeacon\run_paam_dl_reg.bat")    # Must args

# parse args
args = parser.parse_args()

# Logging configuration
logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")

# Device credentials
DEVICE_CREDENTIALS = {
    "SanDiego_Server": {"ip": "172.22.0.12", "username": "labuser", "password": "1234"},
    "RS_ngp800": {"ip": "172.22.2.12"}, # "username": "Instrument", "password": "instrument"
    "RS_spectrum_analyzer": {"ip": "172.22.0.70", "username": "Instrument", "password": "894129"},
    "keysight_psg": {"ip": "172.22.2.31", "username": "Instrument", "password": "instrument"},
    "RS_signal_generator_smw200a": {"ip": "172.22.2.23", "username": "Instrument", "password": "instrument"},
    "jump_server_ip": "10.18.177.82",
}

# Flag to track the initialization state
initialized = False

# 最大再接続回数を設定
MAX_RETRIES = 0

def reconnect_if_inactive(target_client, jump_username):
    """SSHセッションがアクティブでない場合、再接続を試みる"""
    retries = 0
    while not target_client.get_transport().is_active() and retries < MAX_RETRIES:
        logging.warning("SSH session is inactive, reconnecting...")
        try:
            target_client = connect_through_jump_server(
                DEVICE_CREDENTIALS["jump_server_ip"],
                jump_username,
                DEVICE_CREDENTIALS["SanDiego_Server"]["ip"],
                DEVICE_CREDENTIALS["SanDiego_Server"]["username"],
            )
            logging.info("Reconnected successfully.")
            sleep(5)  # 再接続後に少し待機して安定を待つ
            return target_client
        except Exception as e:
            retries += 1
            logging.error(f"Reconnection attempt {retries} failed: {e}", exc_info=True)
            if retries >= MAX_RETRIES:
                logging.error("Maximum reconnection attempts reached, exiting.")
                sys.exit(1)
    return target_client

def initialize(location, mode):
    """Initialization process (Step 1-7)"""
    global initialized

    try:
        if location == "2":  # Japan - Connect through Jump Server
            logging.info("Japan location selected")
            jump_username = "00210404361"  # 固定
            logging.info("Connecting through jump server")
            target_client = connect_through_jump_server(
                DEVICE_CREDENTIALS["jump_server_ip"],
                jump_username,
                DEVICE_CREDENTIALS["SanDiego_Server"]["ip"],
                DEVICE_CREDENTIALS["SanDiego_Server"]["username"],
            )
        elif location == "1":  # US - Connect directly to Cato client
            logging.info("US location selected")
            logging.info("Connecting directly to Cato client")
            target_client = connect_to_SanDiego_Server(
                DEVICE_CREDENTIALS["SanDiego_Server"]["ip"],
                DEVICE_CREDENTIALS["SanDiego_Server"]["username"],
            )

        # Check and reconnect if session is inactive
        target_client = reconnect_if_inactive(target_client, "00210404361")

        # Run the batch script and check if it was successful
        batch_script_success = run_batch_script(target_client, args.batch)
        if not batch_script_success:
            logging.error("Batch script failed, returning to Step 1 to retry...")
            return  # 失敗した場合は終了して再試行

        # Continue with the other steps (3-7)
        logging.info("Proceeding to Step 3-7...")

        # Step 3: Test NGP-800 connection before proceeding to Step 3
        target_client = reconnect_if_inactive(target_client, "00210404361")
        control_ngp800(DEVICE_CREDENTIALS["RS_ngp800"]["ip"],target_client)

        # Step 4: Run PAAM script
        run_paam_script(args.paam)

        # Step 5: Configure Keysight PSG
        configure_keysight_psg(DEVICE_CREDENTIALS["keysight_psg"])

        # Step 6: Configure R&S SMW200A
        configure_r_and_s_smw200a(DEVICE_CREDENTIALS["RS_signal_generator_smw200a"])

        # Step 7: Connect Spectrum Analyzer
        connect_spectrum_analyzer(DEVICE_CREDENTIALS["RS_spectrum_analyzer"])

    except Exception as e:
        logging.error(f"Initialization failed: {e}", exc_info=True)
        sys.exit(1)

def main():
    global initialized
    try:
        location = "2"  # location を "2" に固定（日本）
        mode = "1"  # mode を "1" に固定

        # Uncomment and modify for user selection when needed
        # location = input("Select location (1: US, 2: Japan): ").strip()
        # mode = input("Select mode (1: Initialization, 2: Measurement): ").strip()

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
