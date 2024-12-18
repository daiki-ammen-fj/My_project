#!python3.11
# step2_run_batch.py

import logging
import sys
import time
import subprocess

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
    handlers=[logging.StreamHandler(sys.stdout)],
)

def run_batch_script(batch_script_path, timeout=3):
    """
    Executes the specified batch script on the target system.

    Args:
        batch_script_path (str): Path to the batch script to be executed.
        timeout (int): Time in seconds to wait before timing out the command.
    
    Returns:
        bool: True if the script executed successfully, False otherwise.
    """
    logging.info(f"Running batch script: {batch_script_path}")
    time.sleep(1)

    try:
        # Run the batch file with shell=True to execute the script
        process = subprocess.Popen(
            batch_script_path, 
            shell=True,  # Necessary to execute batch files
            stdout=subprocess.PIPE, 
            stderr=subprocess.PIPE
        )

        # Wait for the process to complete or time out
        stdout, stderr = process.communicate(timeout=timeout)

        # Capture and log the output and error
        if stdout:
            logging.info("Batch script output:\n" + stdout.decode('utf-8'))
        else:
            logging.info("No output from the batch script.")

        if stderr:
            logging.error("Batch script error:\n" + stderr.decode('utf-8'))
        else:
            logging.info("No error from the batch script.")

        # Check if the batch script was successful
        exit_status = process.returncode
        if exit_status != 0:
            logging.error(f"Batch script failed with exit status: {exit_status}")
            return False

        logging.info("Batch script executed successfully.")
        return True

    except subprocess.TimeoutExpired:
        logging.error(f"Batch script timed out after {timeout} seconds.")
        return False
    except FileNotFoundError:
        logging.error(f"Batch script not found at: {batch_script_path}")
        return False
    except Exception as e:
        logging.error(f"Failed to run batch script: {e}")
        return False


# Step 2 Execution
if __name__ == "__main__":
    BATCH_SCRIPT_PATH = r"C:\Users\labuser\qlight-control\dammy_batch\run_qlight_check.bat"  # Path to the batch script

    # Run the batch script
    success = run_batch_script(BATCH_SCRIPT_PATH)
    if not success:
        logging.error("Batch script execution failed.")
    else:
        logging.info("Batch script executed successfully.")
