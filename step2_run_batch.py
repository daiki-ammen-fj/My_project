#!python3.11
# step2_run_batch.py

import subprocess
import logging

# Set up logging
logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")

def run_batch_script(script_path):
    logging.info("Step 2: Running batch script...")
    try:
        # Run the batch script using subprocess
        subprocess.run([script_path], shell=True, check=True)
        logging.info(f"Batch script executed successfully: {script_path}")
    except subprocess.CalledProcessError as e:
        logging.error(f"Failed to run batch script: {e}")
        logging.error(f"Return code: {e.returncode}, Output: {e.output}, Error: {e.stderr}")
        raise  # Re-raise the exception to propagate the error
