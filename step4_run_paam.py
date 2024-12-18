#!python3.11
# step4_run_batch.py

import logging
import sys
import time
import subprocess

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
    handlers=[logging.StreamHandler(sys.stdout)],
)

def run_paam_script(batch_script_path, timeout=3):
    """
    Executes the specified PAAM batch script on the target system.

    Args:
        batch_script_path (str): Path to the batch script to be executed.
        timeout (int): Time in seconds to wait before timing out the command.
    
    Returns:
        bool: True if the script executed successfully, False otherwise.
    """
    logging.info(f"Running PAAM batch script: {batch_script_path}")
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
            logging.info("PAAM batch script output:\n" + stdout.decode('utf-8'))
        else:
            logging.info("No output from the PAAM batch script.")

        if stderr:
            logging.error("PAAM batch script error:\n" + stderr.decode('utf-8'))
        else:
            logging.info("No error from the PAAM batch script.")

        # Check if the batch script was successful
        exit_status = process.returncode
        if exit_status != 0:
            logging.error(f"PAAM batch script failed with exit status: {exit_status}")
            return False

        logging.info("PAAM batch script executed successfully.")
        return True

    except subprocess.TimeoutExpired:
        logging.error(f"PAAM batch script timed out after {timeout} seconds.")
        return False
    except FileNotFoundError:
        logging.error(f"PAAM batch script not found at: {batch_script_path}")
        return False
    except Exception as e:
        logging.error(f"Failed to run PAAM batch script: {e}")
        return False


# Step 4 Execution
if __name__ == "__main__":
    # Get the batch file path from the command-line arguments (or set default if not provided)
    if len(sys.argv) < 2:
        logging.error("No PAAM batch file provided as an argument.")
        sys.exit(1)

    batch_script_path = sys.argv[1]  # Expecting the PAAM batch script path as the first argument

    # Run the batch script
    success = run_paam_script(batch_script_path)
    if not success:
        logging.error("PAAM batch script execution failed.")
    else:
        logging.info("PAAM batch script executed successfully.")
