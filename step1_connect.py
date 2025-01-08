#!python3.11
# step1_connect.py

import logging
import subprocess
import platform

def check_device_connection(device_ip):
    """Check if the device IP address is reachable on the network."""
    try:
        # Set ping command based on the operating system
        if platform.system().lower() == "windows":
            ping_command = ['ping', '-n', '2', device_ip]  # Use -n for count on Windows
        else:
            ping_command = ['ping', '-c', '2', device_ip]  # Use -c for count on Linux/Mac

        response = subprocess.run(
            ping_command,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            timeout=3  # Set timeout to 3 seconds
        )
        
        if response.returncode == 0:
            logging.info(f"Device {device_ip} is reachable and connection verified.")
            return True
        else:
            logging.error(f"Device {device_ip} is not reachable.")
            return handle_connection_error(device_ip)  # Provide options in case of error
    except subprocess.TimeoutExpired:
        logging.error(f"Ping to {device_ip} timed out.")
        return handle_connection_error(device_ip)  # Provide options in case of error
    except Exception as e:
        logging.error(f"Failed to ping {device_ip}: {e}")
        return handle_connection_error(device_ip)  # Provide options in case of error

def handle_connection_error(device_ip):
    """Prompt the user for options in case of connection errors."""
    user_input = input(f"Failed to reach {device_ip}. Do you want to continue the process? (y/n): ").strip().lower()
    if user_input == 'y':
        logging.info("Proceeding with the next steps despite the connection issue.")
        return True
    else:
        logging.info("Aborting the process due to connection failure.")
        return False
