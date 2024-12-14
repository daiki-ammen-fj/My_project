#!python3.11 
# step5_psg.py

from instrument_lib import KS_PSG
from time import sleep  # Import sleep to wait for 1 second

def configure_keysight_psg(ip):
    print("Step 4: Initializing the Keysight PSG signal generator...")
    sig_gen = KS_PSG(ip_address=ip)  # Connect to the signal generator using the provided IP address
    
    try:
        # Connect to the signal generator
        sig_gen.connect()
        print(f"Connected successfully! Device info: {sig_gen.identification}")

        # Set the frequency to 122.8 MHz
        target_frequency = 122.8e6  # 122.8 MHz
        print(f"Setting the frequency to {target_frequency / 1e6:.1f} MHz...")
        sig_gen.set_freq(target_frequency)
        measured_frequency = sig_gen.get_freq()
        print(f"Frequency set to: {measured_frequency / 1e6:.1f} MHz.")

        # Set the amplitude to -20 dBm
        target_amplitude = -20  # -20 dBm
        print(f"Setting the amplitude to {target_amplitude} dBm...")
        sig_gen.set_amplitude(target_amplitude)
        measured_amplitude = sig_gen.get_amplitude()
        print(f"Amplitude set to: {measured_amplitude} dBm.")

        # Enable the RF output
        print("Enabling the RF output...")
        sig_gen.rf_switch('ON')  # Turn on the RF output
        print("RF output enabled successfully.")

        # Wait for 1 second
        sleep(1)

        # Get the current power output after enabling
        current_power = sig_gen.get_power()  # Get the current power in dBm
        print(f"Current output power: {current_power} dBm.")

        print("Keysight PSG control command executed successfully.")
    
    except Exception as e:
        print(f"Failed to configure Keysight PSG: {e}")
        raise

if __name__ == "__main__":
    # Directly specify the IP address
    ip = "172.22.2.31"  # Replace this with the desired IP address

    configure_keysight_psg(ip)
