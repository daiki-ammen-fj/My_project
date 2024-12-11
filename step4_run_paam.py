# step4_run_paam.py

import logging
import subprocess

# Set up logging
logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")

def run_paam_script(script_path):
    logging.info(f"Step 4: Running PAAM download script at {script_path}...")
    try:
        subprocess.run([script_path], shell=True, check=True)
        logging.info("PAAM script executed successfully.")
    except subprocess.CalledProcessError as e:
        logging.error(f"Failed to run PAAM script: {e}")
        raise  # Re-raise the exception to propagate the error
