#!python3.11
# step5_psg.py

from instrument_lib import KS_PSG

def configure_keysight_psg(ip):
    print("Step 5: Initializing the Keysight PSG signal generator...")
    sig_gen = KS_PSG(ip_address=ip)
    try:
        sig_gen.connect()
        print(f"Connected successfully! Device info: {sig_gen.identification}")

        target_frequency = 122.8e6  # 122.8 MHz
        print(f"Setting the frequency to {target_frequency / 1e6:.1f} MHz...")
        sig_gen.set_freq(target_frequency)
        measured_frequency = sig_gen.get_freq()
        print(f"Frequency set to: {measured_frequency / 1e6:.1f} MHz.")

        target_amplitude = -20  # -20 dBm
        print(f"Setting the amplitude to {target_amplitude} dBm...")
        sig_gen.set_amplitude(target_amplitude)
        measured_amplitude = sig_gen.get_amplitude()
        print(f"Amplitude set to: {measured_amplitude} dBm.")

        print("Keysight PSG control command executed successfully.")
    except Exception as e:
        print(f"Failed to configure Keysight PSG: {e}")
        raise
