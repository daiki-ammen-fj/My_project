# step3_ngp800.py

from instrument_lib import RS_NGPx
from time import sleep

def control_ngp800(ip):
    print("Step 3: Connecting to NGP800 Power Supply...")
    power_supply = RS_NGPx(ip_address=ip)
    try:
        power_supply.connect()
        print(f"Connected successfully! Device info: {power_supply.identification}")

        target_current = 2.0  # 2 Amperes
        print(f"Setting current to {target_current} A on channel 1...")
        power_supply.set_current(1, target_current)
        sleep(1)  # 1 second wait
        current = power_supply.get_current(1)
        print(f"Measured Current on Channel 1: {current} A")
        assert current == target_current, "Current mismatch!"

        target_voltage = 1.1  # 1.1 Volts
        print(f"Setting voltage to {target_voltage} V on channel 1...")
        power_supply.set_voltage(1, target_voltage)
        sleep(1)  # 1 second wait
        voltage = power_supply.get_voltage(1)
        print(f"Measured Voltage on Channel 1: {voltage} V")
        assert voltage == target_voltage, "Voltage mismatch!"

        print("Turning ON power for Channel 1...")
        power_supply.toggle_channel_output_state(1, 1)

        print("NGP800 control command executed successfully.")
    except Exception as e:
        print(f"Failed to control NGP800: {e}")
        raise
