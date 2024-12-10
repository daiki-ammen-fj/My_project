# main.py

from step1_connect import connect_to_cato_client
from step2_run_batch import run_batch_script
from step3_ngp800 import control_ngp800
from step4_run_paam import run_paam_script
from step5_psg import configure_keysight_psg
from step6_smw200a import configure_r_and_s_smw200a
from step7_signal_analyzer import connect_signal_analyzer
from time import sleep

# Device credentials and IP addresses
DEVICE_CREDENTIALS = {
    "cato_client": {"ip": "172.22.0.12", "password": "1234"},
    "tightvnc_ngp800": {"ip": "172.22.2.12"},
    "tightvnc_signal_analyzer": {"ip": "172.22.0.51", "password": "894129"},
    "keysight_psg": {"ip": "172.22.2.35"},
    "r_and_s_smw200a": {"url": "http://172.22.2.31", "password": "instrum"}
}

def main():
    try:
        # Step 1: Connect to Cato client
        connect_to_cato_client(DEVICE_CREDENTIALS["cato_client"]["ip"], DEVICE_CREDENTIALS["cato_client"]["password"])

        # Step 2: Run the batch script
        run_batch_script(r"C:\Users\labuser\qlight-control\run_qlight_check.bat")

        # Step 3: Control the NGP800 power supply
        control_ngp800(DEVICE_CREDENTIALS["tightvnc_ngp800"]["ip"])

        # Step 4: Run the PAAM download script
        sleep(10)
        run_paam_script(r"C:\Users\labuser\pybeacon\run_paam_dl_reg.bat")

        # Step 5: Configure Keysight PSG
        configure_keysight_psg(DEVICE_CREDENTIALS["keysight_psg"]["ip"])

        # Step 6: Configure R&S SMW200A
        configure_r_and_s_smw200a(DEVICE_CREDENTIALS["r_and_s_smw200a"]["url"], DEVICE_CREDENTIALS["r_and_s_smw200a"]["password"])

        # Step 7: Connect to the signal analyzer
        connect_signal_analyzer(DEVICE_CREDENTIALS["tightvnc_signal_analyzer"]["ip"], DEVICE_CREDENTIALS["tightvnc_signal_analyzer"]["password"])

    except Exception as e:
        print(f"Process failed: {e}")
        exit(1)

if __name__ == "__main__":
    main()
