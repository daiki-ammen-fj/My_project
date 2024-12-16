#!python3.11
# step2_run_batch.py

import paramiko
import logging
import sys
import time

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
    handlers=[logging.StreamHandler(sys.stdout)],
)

def run_batch_script(target_client, batch_script_path):
    """
    Executes the specified batch script on the target server.

    Args:
        target_client (paramiko.SSHClient): The SSH client connected to the target server.
        batch_script_path (str): Path to the batch script to be executed.
    """
    logging.info(f"Running batch script: {batch_script_path}")

    try:
        # Run the batch file on the target server
        stdin, stdout, stderr = target_client.exec_command(f'cmd.exe /c "{batch_script_path}"')
        result = stdout.read().decode().strip()
        error = stderr.read().decode().strip()

        if error:
            logging.error(f"Error during batch script execution: {error}")
            raise Exception(f"Error during batch script execution: {error}")

        logging.info(f"Batch script executed successfully. Output: {result}")
    except Exception as e:
        logging.error(f"Failed to run batch script: {e}")
        raise

def verify_and_run_batch_script(target_client, target_dir, batch_script_path):
    """
    Verifies the target directory exists and then runs the batch script.

    Args:
        target_client (paramiko.SSHClient): The SSH client connected to the target server.
        target_dir (str): The directory to verify.
        batch_script_path (str): The path to the batch script to be executed.
    """
    logging.info(f"Checking if target directory exists: {target_dir}")

    # Check if the target directory exists
    stdin, stdout, stderr = target_client.exec_command(f'if exist "{target_dir}" echo Directory exists')
    result = stdout.read().decode().strip()
    error = stderr.read().decode().strip()

    if error:
        logging.error(f"Error during directory check: {error}")
        raise Exception(f"Error during directory check: {error}")

    if result != "Directory exists":
        raise Exception(f"Target directory does not exist: {target_dir}")

    # Comment this section out to only check the directory without running the batch script
    # Once directory is verified, run the batch script
    logging.info(f"Setting current directory to: {target_dir}")
    # run_batch_script(target_client, batch_script_path)

# Step 2 Execution
if __name__ == "__main__":
    # Using already established SSH connection from Step 1
    TARGET_CLIENT = None  # Replace with the actual target_client from Step 1
    TARGET_DIR = r"C:\Users\labuser\qlight-control"  # Directory where the batch file is located
    BATCH_SCRIPT_PATH = r"C:\Users\labuser\qlight-control\run_qlight_check.bat"  # Path to the batch script

    # Verify the target directory and run the batch script
    if TARGET_CLIENT:
        verify_and_run_batch_script(TARGET_CLIENT, TARGET_DIR, BATCH_SCRIPT_PATH)
    else:
        logging.error("No SSH connection found. Please ensure Step 1 establishes the connection.")
