import logging
import sys, argparse
from time import sleep
from step1_connect import check_device_connection 
from step2_run_batch import run_batch_script
from step3_ngp800 import control_ngp800
from step4_run_paam import run_paam_script
from step5_psg import configure_keysight_psg
from step6_smw200a import configure_r_and_s_smw200a
from step7_spectrum_analyzer import connect_spectrum_analyzer
# from measurement_module.measurement import perform_measurements, initialize_instruments


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
    "RS_ngp800": {"ip": "172.22.2.12"}, # "username": "Instrument", "password": "instrument"
    "RS_spectrum_analyzer": {"ip": "172.22.0.70", "username": "Instrument", "password": "894129"},
    "keysight_psg": {"ip": "172.22.2.31", "username": "Instrument", "password": "instrument"},
    "RS_signal_generator_smw200a": {"ip": "172.22.2.23", "username": "Instrument", "password": "instrument"},
}

# Flag to track the initialization state
initialized = False

def initialize():
    """Initialization process (Step 1-7)"""
    global initialized

    try:
        # Step 1: Check device connection
        for device, credentials in DEVICE_CREDENTIALS.items():
            device_ip = credentials.get("ip")
            if not check_device_connection(device_ip):
                logging.error(f"Initialization failed: {device} is not reachable.")
                return  # 1つでもデバイスが到達不可能なら処理を中断

        # Step 2: Run the batch script and check if it was successful
        batch_script_success = run_batch_script(args.batch)
        if not batch_script_success:
            logging.error("Batch script failed, returning to Step 1 to retry...")
            return  # 失敗した場合は終了して再試行

        # Continue with the other steps (3-7)
        logging.info("Proceeding to Step 3-7...")

        # Step 3: Test NGP-800 connection before proceeding to Step 3
        control_ngp800(DEVICE_CREDENTIALS["RS_ngp800"]["ip"])

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

if __name__ == "__main__":
    try:
        initialize()  # ここで initialize 関数だけを実行
    except Exception as e:
        logging.error(f"Unexpected error: {e}", exc_info=True)
        sys.exit(1)
