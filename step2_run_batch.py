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

def reconnect_if_inactive(target_client):
    """
    Checks if the SSH session is active. If not, attempts to reconnect.
    
    Args:
        target_client (paramiko.SSHClient): The SSH client connected to the target server.
    
    Returns:
        paramiko.SSHClient: Reconnected or original target client.
    """
    if target_client.get_transport() is None or not target_client.get_transport().is_active():
        logging.warning("SSH session is not active. Reconnecting...")
        return None  # Indicates session is not active
    return target_client


def run_batch_script(target_client, batch_script_path, timeout=60):
    """
    Executes the specified batch script on the target server.

    Args:
        target_client (paramiko.SSHClient): The SSH client connected to the target server.
        batch_script_path (str): Path to the batch script to be executed.
        timeout (int): Time in seconds to wait before timing out the command.
    
    Returns:
        bool: True if the script executed successfully, False otherwise.
    """
    logging.info(f"Running batch script: {batch_script_path}")
    time.sleep(1)

    try:
        # Check if SSH session is active, if not we will reconnect
        target_client = reconnect_if_inactive(target_client)
        if not target_client:
            return False  # SSH session was not active, return failure

        # Run the batch file on the target server
        stdin, stdout, stderr = target_client.exec_command(f'cmd.exe /c "{batch_script_path}"')

        # Set a timeout for reading the output/error
        stdout.channel.settimeout(timeout)
        stderr.channel.settimeout(timeout)

        # Wait for the command to finish, this will block until the command finishes or timeout occurs
        exit_status = None
        start_time = time.time()
        while time.time() - start_time < timeout:
            # Capture the output and error from the command
            output = stdout.channel.recv(1024).decode('utf-8')
            if output:
                logging.info(output)

            error = stderr.channel.recv(1024).decode('utf-8')
            if error:
                logging.error(error)

            if stdout.channel.exit_status_ready():
                exit_status = stdout.channel.recv_exit_status()
                break

            time.sleep(1)

        if exit_status is None:
            logging.error(f"Batch script timed out after {timeout} seconds.")
            return False

        logging.info(f"Batch script exit status: {exit_status}")

        if exit_status != 0:
            logging.error(f"Batch script failed with exit status: {exit_status}")
            return False

        logging.info("Batch script executed successfully.")
        return True

    except paramiko.SSHException as e:
        logging.error(f"SSH error during batch script execution: {e}")
        return False  # Return False on SSH errors
    except Exception as e:
        logging.error(f"Failed to run batch script: {e}")
        return False  # Return False on other errors


# Step 2 Execution
if __name__ == "__main__":
    TARGET_CLIENT = None  # Replace with the actual target_client from Step 1
    BATCH_SCRIPT_PATH = r"C:\Users\labuser\qlight-control\dammy_batch\run_qlight_check.bat"  # Path to the batch script

    # Here, the TARGET_CLIENT should be the same object passed from Step 1
    if TARGET_CLIENT:
        success = run_batch_script(TARGET_CLIENT, BATCH_SCRIPT_PATH)
        if not success:
            logging.error("Batch script execution failed.")
    else:
        logging.error("No SSH connection found. Please ensure Step 1 establishes the connection.")
