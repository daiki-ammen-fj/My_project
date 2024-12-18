#!python3.11  
# step1_connect.py

import paramiko
import logging
import sys
import time

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
    handlers=[logging.StreamHandler(sys.stdout)],
)

def connect_to_SanDiego_Server(ip, username, retries=0, timeout=10, key_filename=None, port=22):
    """
    Connect to the Cato client via SSH on a Windows machine using SSH key authentication.

    Args:
        ip (str): Cato client's IP address.
        username (str): SSH username.
        retries (int): Number of connection retries.
        timeout (int): Connection timeout in seconds.
        key_filename (str): Path to the private key file for SSH authentication.
        port (int): SSH port (default is 22).

    Raises:
        Exception: If SSH connection fails after retries.
    """
    logging.info("Step 1: Connecting to Cato client...")

    ssh_client = None
    for attempt in range(1, retries + 1):
        try:
            ssh_client = paramiko.SSHClient()
            ssh_client.set_missing_host_key_policy(paramiko.AutoAddPolicy())

            # Use SSH key for authentication (no password)
            if key_filename:
                ssh_client.connect(ip, username=username, key_filename=key_filename, port=port, timeout=timeout)
            else:
                ssh_client.connect(ip, username=username, port=port, timeout=timeout)

            logging.info(f"Successfully connected to Cato client at {ip} on attempt {attempt}.")
            
            # Confirm current directory
            stdin, stdout, stderr = ssh_client.exec_command('cd')
            current_dir = stdout.read().decode().strip()
            logging.info(f"Current directory after connection: {current_dir}")

            return ssh_client  # Return the ssh_client object for further use

        except paramiko.AuthenticationException:
            logging.error(f"Authentication failed for {ip}. Check SSH key.")
            break  # Authentication failure should not retry
        except (paramiko.SSHException, Exception) as e:
            logging.error(f"Error during SSH connection to {ip} on attempt {attempt}: {e}")
        
        logging.warning(f"Retrying SSH connection ({attempt}/{retries})...")
        time.sleep(2)  # Wait before retrying

    if ssh_client:
        ssh_client.close()

    raise Exception("SSH connection to Cato client failed after retries.")


def connect_through_jump_server(
    jump_server_ip, jump_server_username, target_ip, target_username, retries=3, port=22
):
    """
    Connect to the target server through the jump server using paramiko SSH.

    Args:
        jump_server_ip (str): Jump server IP address.
        jump_server_username (str): Jump server SSH username.
        target_ip (str): Target server IP address.
        target_username (str): Target server SSH username.
        retries (int): Number of connection retries.
        port (int): SSH port (default is 22).

    Returns:
        paramiko.SSHClient: Connected target server client.
    """
    for attempt in range(1, retries + 1):
        try:
            # Connect to the jump server
            logging.info(f"Connecting to jump server: {jump_server_ip}")
            jump_client = paramiko.SSHClient()
            jump_client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
            jump_client.connect(jump_server_ip, username=jump_server_username, port=port)

            # Use jump server to connect to the target server
            logging.info("Connecting to target server via jump server...")
            jump_transport = jump_client.get_transport()
            jump_channel = jump_transport.open_channel(
                "direct-tcpip", (target_ip, port), (jump_server_ip, 0)
            )

            target_client = paramiko.SSHClient()
            target_client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
            target_client.connect(target_ip, username=target_username, sock=jump_channel)

            logging.info("Successfully connected to target server via jump server.")
            return target_client  # Return the target client for further use

        except paramiko.AuthenticationException:
            logging.error(f"Authentication failed for {jump_server_ip} or {target_ip}. Check credentials.")
            break  # Authentication failure should not retry
        except Exception as e:
            logging.error(f"Error during SSH connection: {e}")
        
        logging.warning(f"Retrying SSH connection ({attempt}/{retries})...")
        time.sleep(2)  # Wait before retrying

    raise Exception("SSH connection to target server via jump server failed after retries.")


# Example usage
if __name__ == "__main__":
    JUMP_SERVER_IP = "10.18.177.82"
    JUMP_SERVER_USERNAME = "00210404361"
    TARGET_IP = "172.22.0.12"
    TARGET_USERNAME = "labuser"

    target_client = connect_through_jump_server(
        JUMP_SERVER_IP, JUMP_SERVER_USERNAME, TARGET_IP, TARGET_USERNAME
    )

    # Perform further actions on the target server
    target_client.close()
