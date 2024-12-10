# measurement.py

# Import necessary libraries for controlling RS_FSx (Signal and Spectrum Analyzer) and RS_SMx (Signal Generator)
import time

def set_center_frequency(rs_fsx, frequency=28.01712e9):
    """Set the center frequency of RS_FSx to a fixed value (28.01712 GHz)."""
    # Set the center frequency to 28.01712 GHz
    rs_fsx.write(f"FREQ:CENT {frequency}")
    print(f"Center frequency set to {frequency / 1e9} GHz.")

def load_quicksave(rs_fsx, quicksave_num=6):
    """Load the quicksave template 'quicksave 6' into RS_FSx."""
    # Load the quicksave template 6
    rs_fsx.write(f"MMEM:LOAD 'quicksave{quicksave_num}.sav'")
    print(f"Loaded quicksave {quicksave_num}.")

def change_power_and_measure(rs_sm, rs_fsx, start_power, end_power, step=1):
    """Change the input power of RS_SMx and measure the EVM at each power level."""
    # List to store the power and corresponding EVM results
    power_points = []
    
    # Change the power from start_power to end_power in steps of 1 dBm
    for power in range(start_power, end_power + 1, step):
        rs_sm.write(f"POW:AMPL {power} dBm")  # Set the output power of the signal generator
        time.sleep(1)  # Wait for the power setting to take effect
        
        # Measure EVM using RS_FSx
        evm = rs_fsx.query("CALC:MARK:RES:EVM?")  # Query the EVM value
        print(f"I/P Power = {power} dBm, EVM = {evm}%")
        
        # Record the power and EVM in a dictionary and append it to the list
        power_points.append({
            "input_power": power,
            "evm": evm
        })
    
    return power_points

def perform_measurements(rs_sm, rs_fsx):
    """Perform the full measurement process."""
    
    # a: Set the center frequency to 28.01712 GHz
    set_center_frequency(rs_fsx, 28.01712e9)  # Set the center frequency to 28.01712 GHz
    
    # b: Load the quicksave template 6
    load_quicksave(rs_fsx, 6)
    
    # c: Change power and measure EVM across a range of powers
    power_points = change_power_and_measure(rs_sm, rs_fsx, start_power=-39, end_power=-11, step=1)
    
    return power_points
