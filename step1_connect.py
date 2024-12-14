#!python3.11
# step1_connect.py

import paramiko
import logging
import time
import sys

# Connection from US Laptop is currently being debugged
def connect_to_cato_client(ip, username, retries=3, timeout=10, key_filename=None, port=22):
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
    try:
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

    finally:
        if ssh_client:
            ssh_client.close()

    raise Exception("SSH connection to Cato client failed after retries.")


def connect_through_jump_server(jump_server_ip, jump_server_username, target_ip, target_username, port=22):
    """
    Connect to the target server through the jump server using paramiko SSH.

    Args:
        jump_server_ip (str): Jump server IP address.
        jump_server_username (str): Jump server SSH username.
        target_ip (str): Target server IP address.
        target_username (str): Target server SSH username.
        port (int): SSH port (default is 22).
    """
    logging.info("Step 1: Connecting to Cato client...")
    try:
        # Connect to the jump server
        jump_client = paramiko.SSHClient()
        jump_client.set_missing_host_key_policy(paramiko.AutoAddPolicy())

        logging.info(f"Connecting to jump server: {jump_server_ip}")
        jump_client.connect(jump_server_ip, username=jump_server_username, port=port)

        # Use jump server to create an SSH connection to the target server
        jump_transport = jump_client.get_transport()
        dest_addr = (target_ip, port)
        local_addr = (jump_server_ip, port)
        jump_channel = jump_transport.open_channel('direct-tcpip', dest_addr, local_addr)

        # Connect to the target server via jump server channel
        target_client = paramiko.SSHClient()
        target_client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        target_client.connect(target_ip, username=target_username, sock=jump_channel)

        # Log success for both jump server and target server connection
        logging.info("Successfully connected to target server via jump server.")

        # Optionally, execute a command on the target server (e.g., retrieve hostname)
        stdin, stdout, stderr = target_client.exec_command('cd')  # For Windows, 'cd' will show the current directory
        current_dir = stdout.read().decode().strip()
        logging.info(f"Current directory on target server: {current_dir}")

        # Close the target client
        target_client.close()

    except paramiko.AuthenticationException:
        logging.error(f"Authentication failed for {jump_server_ip} or {target_ip}. Check username/password.")
    except (paramiko.SSHException, Exception) as e:
        logging.error(f"Error during SSH connection: {e}")
        sys.exit(1)  # Exit the program if connection fails
    finally:
        jump_client.close()
