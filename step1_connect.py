# step1_connect.py


import paramiko
import subprocess
import logging
import time

def connect_to_cato_client(ip, username, password, retries=1, timeout=10):
    logging.info("Step 1: Connecting to Cato client...")

    # Retry loop for connection attempts (only 1 attempt now)
    attempt = 0
    while attempt < retries:
        try:
            # Initialize SSH client and set timeout
            ssh_client = paramiko.SSHClient()
            ssh_client.set_missing_host_key_policy(paramiko.AutoAddPolicy())  # Automatically add missing host keys
            ssh_client.connect(ip, username=username, password=password, timeout=timeout)

            logging.info(f"Successfully connected to Cato client at {ip}")
            
            # If SSH connection is successful, attempt to connect to TightVNC
            connect_to_vnc(ip, password)
            ssh_client.close()  # Close the SSH connection
            return  # Exit after successful connection

        except paramiko.AuthenticationException:
            logging.error(f"Authentication failed when connecting to {ip}")
            break  # Exit on authentication failure
        except paramiko.SSHException as e:
            logging.error(f"SSH error occurred when connecting to {ip}: {e}")
            break  # Exit on SSH error
        except Exception as e:
            logging.error(f"Unexpected error: {e}")
            break  # Exit on any other unexpected error

        # Increment the attempt counter (this will be 1 in this case)
        attempt += 1
        logging.warning(f"Retrying ({attempt}/{retries})...")

    raise Exception("Connection failed after 1 attempt.")  # Stop execution if failed

def connect_to_vnc(ip, password, retries=1, timeout=10):
    logging.info(f"Step 1: Connecting to TightVNC at {ip}...")

    attempt = 0
    while attempt < retries:
        try:
            # Call the TightVNC client to establish the connection
            vnc_command = f"vncviewer {ip}:5900"  # Default VNC port is usually 5900
            result = subprocess.run([vnc_command, "-password", password], check=True, timeout=timeout)

            # Check the result of the VNC connection
            if result.returncode == 0:
                logging.info(f"Successfully connected to VNC at {ip}")
                return  # Return successfully if connection was made
            else:
                logging.error(f"VNC connection failed with return code {result.returncode}")
        
        except subprocess.TimeoutExpired:
            logging.error(f"Timeout expired while connecting to VNC at {ip}")
        except subprocess.CalledProcessError as e:
            logging.error(f"Error occurred while connecting to VNC at {ip}: {e}")
        except Exception as e:
            logging.error(f"Unexpected error while connecting to VNC at {ip}: {e}")

        # Retry the connection
        attempt += 1
        logging.warning(f"Retrying VNC connection ({attempt}/{retries})...")

    raise Exception("Failed to connect to VNC after retries.")  # Stop execution if VNC connection fails
