# measurement.py

# Import necessary libraries for controlling RS_FSx (Signal and Spectrum Analyzer) and RS_SMx (Signal Generator)
import time
import json
import os

class EVMMeasurementError(Exception):
    """Custom exception for EVM measurement errors."""
    pass

def set_center_frequency(rs_fsx, frequency=28.01712e9):
    """Set the center frequency of RS_FSx to a fixed value (28.01712 GHz)."""
    rs_fsx.write(f"FREQ:CENT {frequency}")
    print(f"Center frequency set to {frequency / 1e9} GHz.")

def load_quicksave(rs_fsx, quicksave_num=6):
    """Load the quicksave template 'quicksave 6' into RS_FSx."""
    rs_fsx.write(f"MMEM:LOAD 'quicksave{quicksave_num}.sav'")
    print(f"Loaded quicksave {quicksave_num}.")

def find_evm_threshold(rs_sm, rs_fsx, threshold=10, start_power=-39, end_power=-11, step=1):
    """Find the power levels where EVM is below the threshold (e.g., 10%)."""
    power_points = []
    
    for power in range(start_power, end_power + 1, step):
        rs_sm.write(f"POW:AMPL {power} dBm")  # Set the output power of the signal generator
        time.sleep(1)  # Wait for the power setting to take effect
        
        evm = float(rs_fsx.query("CALC:MARK:RES:EVM?"))  # Query the EVM value
        print(f"Power = {power} dBm, EVM = {evm}%")
        
        if evm <= threshold:
            power_points.append({"input_power": power, "evm": evm})
        else:
            print(f"Stopping measurement as EVM exceeded threshold ({threshold}%) at power = {power} dBm.")
            break

    if not power_points:
        raise EVMMeasurementError("EVM is not below the threshold at any power level in the specified range.")
    
    return power_points

def measure_parameters(rs_fsx, path_loss=-56.905):
    """
    Measure additional parameters like CF(dB), O/P Power(dBm), ACLR Lower(dBc), ACLR Upper(dBc).
    Calculate EIRP using the formula: EIRP = O/P Power - Path Loss.
    """
    cf = float(rs_fsx.query("CALC:MARK:RES:CF?"))  # Query the center frequency (CF)
    output_power = float(rs_fsx.query("MEASU:SCAL:POW?"))  # Query the output power (O/P Power)
    aclr_lower = float(rs_fsx.query("CALC:MARK:RES:ACLR:LOWER?"))  # Query ACLR Lower
    aclr_upper = float(rs_fsx.query("CALC:MARK:RES:ACLR:UPPER?"))  # Query ACLR Upper
    eirp = output_power - path_loss  # Calculate EIRP
    return cf, output_power, aclr_lower, aclr_upper, eirp

def change_power_and_measure(rs_sm, rs_fsx, start_power, end_power, step=1, path_loss=-56.905):
    """
    Change the input power of RS_SMx and measure the EVM and other parameters at each power level within a specific range.
    Include Path Loss and EIRP in the measurement data.
    """
    # Find the range where EVM stays below the threshold (10%)
    threshold_points = find_evm_threshold(rs_sm, rs_fsx, threshold=10, start_power=start_power, end_power=end_power, step=step)
    
    # If there are no points found, return an empty list
    if not threshold_points:
        print("No power points found with EVM below threshold.")
        return []

    # Find the optimal power range where EVM stays below threshold
    optimal_range_start = threshold_points[0]["input_power"]
    optimal_range_end = threshold_points[-1]["input_power"]

    print(f"Measuring between {optimal_range_start} dBm and {optimal_range_end} dBm")
    
    all_power_points = []
    for power in range(optimal_range_start, optimal_range_end + 1):
        rs_sm.write(f"POW:AMPL {power} dBm")  # Set the output power of the signal generator
        time.sleep(1)  # Wait for the power setting to take effect
        
        # Measure EVM using RS_FSx
        evm = float(rs_fsx.query("CALC:MARK:RES:EVM?"))  # Query the EVM value
        cf, output_power, aclr_lower, aclr_upper, eirp = measure_parameters(rs_fsx, path_loss)  # Measure other parameters
        
        print(f"Power = {power} dBm, EVM = {evm}%, CF = {cf} dB, O/P Power = {output_power} dBm, ACLR Lower = {aclr_lower} dBc, ACLR Upper = {aclr_upper} dBc, EIRP = {eirp} dBm")
        
        # If EVM exceeds threshold, stop the measurement
        if evm > 10:
            print(f"Stopping measurement as EVM exceeded threshold ({evm}%) at power = {power} dBm.")
            break
        
        # Record the data
        all_power_points.append({
            "input_power": power,
            "evm": evm,
            "cf": cf,
            "output_power": output_power,
            "aclr_lower": aclr_lower,
            "aclr_upper": aclr_upper,
            "path_loss": path_loss,
            "eirp": eirp
        })
    
    return all_power_points

def save_measurement_results(results, filename="measurement_results.json"):
    """Save the measurement results to a JSON file in a specified folder."""
    # Create the directory if it doesn't exist
    directory = os.path.dirname(filename)
    if directory and not os.path.exists(directory):
        os.makedirs(directory)

    # Write the results to the JSON file
    with open(filename, 'w') as json_file:
        json.dump(results, json_file, indent=4)
    print(f"Results saved to {filename}")

def perform_measurements(rs_sm, rs_fsx, save_directory="results"):
    """Perform the full measurement process and save the results."""
    
    # a: Set the center frequency to 28.01712 GHz
    set_center_frequency(rs_fsx, 28.01712e9)  # Set the center frequency to 28.01712 GHz
    
    # b: Load the quicksave template 6
    load_quicksave(rs_fsx, 6)
    
    # c: Find the power levels where EVM stays below 10% and record the data
    try:
        power_points = change_power_and_measure(rs_sm, rs_fsx, start_power=-50, end_power=-5, step=1)
    except EVMMeasurementError as e:
        print(f"Measurement failed: {e}")
        return None
    
    # d: Save the results to a specified directory and filename
    save_filename = os.path.join(save_directory, "measurement_results.json")
    save_measurement_results(power_points, save_filename)
    
    return power_points
