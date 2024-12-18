# Step1_connect.py
import logging
import subprocess

def check_device_connection(device_ip):
    """デバイスのIPアドレスがネットワーク上で到達可能かを確認"""
    try:
        response = subprocess.run(
            ['ping', '-n', '1', device_ip],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True
        )
        if response.returncode == 0:
            logging.info(f"Device {device_ip} is reachable.")
            return True
        else:
            logging.error(f"Device {device_ip} is not reachable.")
            return False
    except Exception as e:
        logging.error(f"Failed to ping {device_ip}: {e}")
        return False
