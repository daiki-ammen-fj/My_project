#!python3.11
# step6_smw200a.py

from instrument_lib import RS_SMx  # Import the instrument driver

def configure_r_and_s_smw200a(url: str, password: str) -> None:
    """Configures the R&S SMW200A signal generator."""

    print("Initializing R&S SMW200A Signal Generator...")

    # Create an instance of the RS_SMx driver
    sig_gen = RS_SMx(ip_address=url)  # Use the URL as the IP address

    # Connect to the signal generator
    print("Connecting to R&S SMW200A Signal Generator...")
    sig_gen.connect()
    print(f"Connected successfully! Device info: {sig_gen.identification}")

    # Set and verify frequency
    target_frequency = 5.16144e9  # 5.16144 GHz
    print(f"Setting frequency to {target_frequency / 1e9:.5f} GHz...")
    sig_gen.set_freq(target_frequency)
    current_frequency = sig_gen.get_freq()
    print(f"Current Frequency: {current_frequency / 1e9:.5f} GHz")
    assert current_frequency == target_frequency, "Frequency mismatch!"

    # Set and verify power level
    target_power_level = -40  # -40 dBm
    print(f"Setting power level to {target_power_level} dBm...")
    sig_gen.set_power_level(target_power_level)
    current_power_level = sig_gen.get_power()
    print(f"Current Power Level: {current_power_level} dBm")
    assert current_power_level == target_power_level, "Power level mismatch!"

    print("Step 6 complete. R&S SMW200A is configured successfully.")

