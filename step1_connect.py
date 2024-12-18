#!python3.11
# step1_connect.py

import logging
import subprocess
import platform

def check_device_connection(device_ip):
    """デバイスのIPアドレスがネットワーク上で到達可能かを確認"""
    try:
        # オペレーティングシステムによってpingコマンドのオプションが異なるため、適切に設定
        if platform.system().lower() == "windows":
            ping_command = ['ping', '-n', '1', device_ip]  # Windowsでは-nで回数指定
        else:
            ping_command = ['ping', '-c', '1', device_ip]  # Linux/Macでは-cで回数指定

        response = subprocess.run(
            ping_command,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            timeout=3  # タイムアウトを5秒に設定
        )
        
        if response.returncode == 0:
            logging.info(f"Device {device_ip} is reachable.")
            return True
        else:
            logging.error(f"Device {device_ip} is not reachable.")
            return handle_connection_error(device_ip)  # エラー時に選択肢を提示
    except subprocess.TimeoutExpired:
        logging.error(f"Ping to {device_ip} timed out.")
        return handle_connection_error(device_ip)  # エラー時に選択肢を提示
    except Exception as e:
        logging.error(f"Failed to ping {device_ip}: {e}")
        return handle_connection_error(device_ip)  # エラー時に選択肢を提示

def handle_connection_error(device_ip):
    """接続エラー時にユーザーに選択肢を提示する"""
    user_input = input(f"Failed to reach {device_ip}. Do you want to continue the process? (y/n): ").strip().lower()
    if user_input == 'y':
        logging.info("Proceeding with the next steps despite the connection issue.")
        return True
    else:
        logging.info("Aborting the process due to connection failure.")
        return False
