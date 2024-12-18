import logging
from RsInstrument import RsInstrument  # Import RsInstrument for NGP800 control
from time import sleep
import paramiko

# Log configuration
logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")

MAX_RETRIES = 1  # Maximum number of reconnection attempts

def reconnect_if_inactive(target_client):
    """SSHセッションがアクティブでない場合、再接続を試みる"""
    retries = 0
    # Check if the SSH session is active
    while target_client.get_transport() is None or not target_client.get_transport().is_active():
        if retries >= MAX_RETRIES:
            logging.error("Maximum reconnection attempts reached, exiting.")
            raise Exception("SSH session inactive and maximum retries exceeded")
        
        retries += 1
        logging.warning(f"SSH session is inactive (attempt {retries}). Reconnecting...")
        try:
            # Reconnect by reusing the existing connection logic, without repeating full connect info
            logging.info("Reconnecting to the target client...")
            target_client.connect("172.22.0.12", username="labuser")  # Use saved details
            logging.info("Reconnected successfully.")
            sleep(5)  # 再接続後に少し待機して安定を待つ
        except Exception as e:
            logging.error(f"Reconnection attempt {retries} failed: {e}", exc_info=True)
            if retries >= MAX_RETRIES:
                raise

    return target_client

def check_ssh_session(target_client):
    """SSHセッションがアクティブか確認する"""
    try:
        if target_client.get_transport() is not None and target_client.get_transport().is_active():
            logging.info("SSH session is active.")
            return True
        else:
            logging.warning("SSH session is inactive.")
            return False
    except Exception as e:
        logging.error(f"Failed to check SSH session: {e}", exc_info=True)
        return False

def control_ngp800(ngp800_ip, target_client):
    """Controls NGP800 from San DiegoPC over LAN"""
    try:
        logging.info("Checking SSH session before proceeding to NGP800 control.")
        if not check_ssh_session(target_client):
            logging.error("SSH session is not active. Exiting...")
            raise Exception("SSH session inactive.")

        logging.info(f"Starting connection to NGP800 at {ngp800_ip}...")

        # LAN connection to NGP800
        ngp = RsInstrument(f"TCPIP::{ngp800_ip}::INSTR", id_query=True, reset=False)

        # Query device information
        device_info = ngp.query_str("*IDN?")
        logging.info(f"NGP800 Information: {device_info}")

        # Enable output on Channel 1
        ngp.write_str("OUTP1 ON")
        logging.info("Channel 1 output enabled.")
        
        sleep(3)
        
        # Measure voltage on Channel 1
        measured_voltage = ngp.query_str("MEAS:VOLT? CH1")
        logging.info(f"Measured Voltage (Channel 1): {measured_voltage}")

        # Query voltage and current limits
        voltage_limit = ngp.query_str("VOLT? CH1")
        current_limit = ngp.query_str("CURR? CH1")
        logging.info(f"Voltage Limit (Channel 1): {voltage_limit}")
        logging.info(f"Current Limit (Channel 1): {current_limit}")

        # Check output state
        output_state = ngp.query_str("OUTP1?")
        logging.info(f"Output State (Channel 1): {output_state}")

        # Disable output after operations
        ngp.write_str("OUTP1 OFF")
        logging.info("Channel 1 output disabled.")

        # Close connection
        ngp.close()
        logging.info("NGP800 connection closed successfully.")
        
    except Exception as e:
        logging.error(f"Error occurred while controlling NGP800: {e}", exc_info=True)

# Main execution part
if __name__ == "__main__":
    logging.info("Starting NGP800 control process.")
    try:
        # Pass the IP address (ngp800_ip) directly to the function
        ngp800_ip = "172.22.2.12"  # Example IP address for NGP800
        target_client = None  # Placeholder for SSH client object
        control_ngp800(ngp800_ip, target_client)

    except Exception as e:
        logging.error("An error occurred during the NGP800 control process.", exc_info=True)
