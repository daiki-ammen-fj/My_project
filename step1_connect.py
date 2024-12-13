#!python3.11
# step1_connect.py

import paramiko
import subprocess
import logging
import time
import sys

def connect_to_cato_client(ip, username, password, retries=3, timeout=10):
    """
    Connect to the Cato client via SSH and then to TightVNC.

    Args:
        ip (str): Cato client's IP address.
        username (str): SSH username.
        password (str): SSH password.
        retries (int): Number of connection retries.
        timeout (int): Connection timeout in seconds.

    Raises:
        Exception: If SSH or TightVNC connection fails after retries.
    """
    logging.info("Step 1: Connecting to Cato client...")

    ssh_client = None
    try:
        for attempt in range(1, retries + 1):
            try:
                # Connect to Cato client via SSH using paramiko (for actual SSH connection)
                ssh_client = paramiko.SSHClient()
                ssh_client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
                ssh_client.connect(ip, username=username, password=password, timeout=timeout)

                logging.info(f"Successfully connected to Cato client at {ip} on attempt {attempt}.")

                # Proceed to connect to TightVNC
                connect_to_vnc(ip, password)
                return  # Exit on success

            except paramiko.AuthenticationException:
                logging.error(f"Authentication failed for {ip}. Check username/password.")
                break  # Authentication failure should not retry
            except (paramiko.SSHException, Exception) as e:
                logging.error(f"Error during SSH connection to {ip} on attempt {attempt}: {e}")

            logging.warning(f"Retrying SSH connection ({attempt}/{retries})...")
            time.sleep(2)  # Wait before retrying

    finally:
        if ssh_client:
            ssh_client.close()

    raise Exception("SSH connection to Cato client failed after retries.")


def connect_to_vnc(ip, password, retries=3, timeout=10):
    """
    Connect to the Cato client using TightVNC.

    Args:
        ip (str): VNC server's IP address.
        password (str): VNC connection password.
        retries (int): Number of connection retries.
        timeout (int): Connection timeout in seconds.

    Raises:
        Exception: If VNC connection fails after retries.
    """
    logging.info(f"Step 2: Connecting to TightVNC at {ip}...")

    for attempt in range(1, retries + 1):
        try:
            vnc_command = ["vncviewer", f"{ip}:5900", "-password", password]
            logging.info(f"Executing command: {' '.join(vnc_command)}")

            result = subprocess.run(vnc_command, check=True, timeout=timeout)

            if result.returncode == 0:
                logging.info(f"Successfully connected to VNC at {ip} on attempt {attempt}")
                return  # Exit on success
            else:
                logging.error(f"VNC connection returned non-zero code {result.returncode}")

        except (subprocess.TimeoutExpired, subprocess.CalledProcessError, Exception) as e:
            logging.error(f"Error during VNC connection to {ip} on attempt {attempt}: {e}")

        logging.warning(f"Retrying VNC connection ({attempt}/{retries})...")
        time.sleep(2)  # Wait before retrying

    raise Exception("TightVNC connection failed after retries.")


def connect_through_jump_server(jump_server_ip, jump_server_username, target_ip, target_username):
    """
    Connect to the target server through the jump server using paramiko SSH.
    """
    logging.info("Attempting to connect to jump server...")

    jump_client = paramiko.SSHClient()
    jump_client.set_missing_host_key_policy(paramiko.AutoAddPolicy())

    try:
        # Connect to the jump server
        logging.info(f"Connecting to jump server: {jump_server_ip}")
        jump_client.connect(jump_server_ip, username=jump_server_username)

        logging.info(f"Successfully connected to jump server: {jump_server_ip}")

        # Use jump server to create an SSH connection to the target server
        jump_transport = jump_client.get_transport()
        dest_addr = (target_ip, 22)
        local_addr = (jump_server_ip, 22)
        jump_channel = jump_transport.open_channel('direct-tcpip', dest_addr, local_addr)

        # Connect to the target server via jump server channel
        target_client = paramiko.SSHClient()
        target_client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        target_client.connect(target_ip, username=target_username, sock=jump_channel)

        logging.info(f"Successfully connected to target server: {target_ip}")

        # You can now interact with the target server (run commands, etc.)
        # Example of running a command on the target server
        stdin, stdout, stderr = target_client.exec_command('hostname')
        logging.info(f"Target server hostname: {stdout.read().decode().strip()}")

        # Optionally, close the target client
        target_client.close()

    except paramiko.AuthenticationException:
        logging.error(f"Authentication failed for {jump_server_ip} or {target_ip}. Check username/password.")
    except (paramiko.SSHException, Exception) as e:
        logging.error(f"Error during SSH connection: {e}")
        sys.exit(1)  # Exit the program if connection fails
    finally:
        jump_client.close()


def main():
    logging.basicConfig(level=logging.INFO)

    # User-defined values
    jump_server_ip = '10.18.177.82'
    jump_server_username = '00210404361'
    target_ip = '172.22.0.12'
    target_username = 'labuser'

    connect_through_jump_server(jump_server_ip, jump_server_username, target_ip, target_username)


if __name__ == '__main__':
    main()
