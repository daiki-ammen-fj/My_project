#!python3.11
# measurement.py

# Import necessary libraries for controlling RS_FSx (Signal and Spectrum Analyzer) and RS_SMx (Signal Generator)
from RsInstrument import RsInstrument
import time
import json
import os
from itertools import product

class EVMMeasurementError(Exception):
    """Custom exception for EVM measurement errors."""
    pass

def load_config(config_file="measurement_config.json"):
    """Load the measurement configuration from the JSON file."""
    with open(config_file, 'r') as file:
        config = json.load(file)
    return config["parameters"]

def prompt_user_for_selection(options, parameter_name):
    """Prompt the user to select one or more options from a list."""
    print(f"Please select {parameter_name} (separate multiple choices with commas):")
    for idx, option in enumerate(options, 1):
        print(f"{idx}: {option}")
    
    user_input = input("Your choice: ")
    selected_indices = [int(idx) - 1 for idx in user_input.split(',') if idx.isdigit()]
    
    return [options[i] for i in selected_indices if 0 <= i < len(options)]

def set_center_frequency(rs_fsx, frequency):
    """Set the center frequency of RS_FSx."""
    rs_fsx.write(f"FREQ:CENT {frequency}")
    print(f"Center frequency set to {frequency} GHz.")

def load_quicksave(rs_fsx, quicksave_num=6):
    """Load the quicksave template 'quicksave 6' into RS_FSx."""
    # Load the quicksave template 6
    rs_fsx.write(f"MMEM:LOAD 'quicksave{quicksave_num}.sav'")
    print(f"Loaded quicksave {quicksave_num}.")

def find_evm_threshold(rs_sm, rs_fsx, config):
    """Find the power levels where EVM is below the threshold."""
    threshold = config["evm_threshold"]
    start_power = config["input_power_range"]["start"]
    end_power = config["input_power_range"]["end"]
    step = config["input_power_range"]["step"]

    power_points = []
    
    # Change the power from start_power to end_power in steps of 1 dBm
    for power in range(start_power, end_power + 1, step):
        rs_sm.write(f"POW:AMPL {power} dBm")  # Set the output power
        time.sleep(1)  # Wait for the power setting to take effect

        evm = float(rs_fsx.query("CALC:MARK:RES:EVM?"))  # Query the EVM value
        print(f"Power = {power} dBm, EVM = {evm}%")

        if evm <= threshold:
            power_points.append({"input_power": power, "evm": evm})
        else:
            print(f"Stopping measurement as EVM exceeded threshold ({threshold}%) at power = {power} dBm.")
            break

    if not power_points:
        raise EVMMeasurementError("EVM is not below the threshold at any power level.")

    return power_points


def measure_parameters(rs_fsx, config):
    """Measure additional parameters like CF, O/P Power, ACLR, and EIRP."""
    path_loss = config["path_loss"]

    cf = float(rs_fsx.query("CALC:MARK:RES:CF?"))  # Center frequency
    output_power = float(rs_fsx.query("MEASU:SCAL:POW?"))  # Output power
    aclr_lower = float(rs_fsx.query("CALC:MARK:RES:ACLR:LOWER?"))  # ACLR Lower
    aclr_upper = float(rs_fsx.query("CALC:MARK:RES:ACLR:UPPER?"))  # ACLR Upper
    eirp = output_power - path_loss  # Calculate EIRP

    return cf, output_power, aclr_lower, aclr_upper, eirp

def initialize_instruments(rs_sm_url, rs_fsx_url):
    """Initialize RS_SMx (Signal Generator) and RS_FSx (Signal Analyzer)."""
    try:
        # Create instances for RS_SMx (Signal Generator) and RS_FSx (Signal Analyzer)
        rs_sm = RsInstrument(f"TCPIP::{rs_sm_url}::INSTR")  # Use the URL as the IP address for RS_SMx
        rs_fsx = RsInstrument(f"TCPIP::{rs_fsx_url}::INSTR")  # Use the URL as the IP address for RS_FSx

        # Connect to the instruments
        print("Connecting to RS_SMx (Signal Generator)...")
        rs_sm.connect()
        print(f"Connected to RS_SMx. Device info: {rs_sm.query('*IDN?')}")

        print("Connecting to RS_FSx (Signal Analyzer)...")
        rs_fsx.connect()
        print(f"Connected to RS_FSx. Device info: {rs_fsx.query('*IDN?')}")

        return rs_sm, rs_fsx
    except Exception as e:
        print(f"Error initializing instruments: {e}")
        raise


def perform_measurements(rs_sm, rs_fsx, config):
    """Perform the full measurement process with all parameter combinations."""
    results = []

    # Get user selections for parameters
    directions = prompt_user_for_selection(config["directions"], "Direction")
    center_frequencies = prompt_user_for_selection([str(freq) for freq in config["center_frequencies"]], "Center Frequency")
    bandwidths = prompt_user_for_selection([str(bw) for bw in config["bandwidths"]], "Bandwidth")
    modulations = prompt_user_for_selection(config["modulation_types"], "Modulation")
    input_powers = prompt_user_for_selection([str(i) for i in range(config["input_power_range"]["start"], config["input_power_range"]["end"] + 1, config["input_power_range"]["step"])], "Input Power")

    # Iterate over all combinations of parameters
    param_combinations = product(
        directions,
        center_frequencies,
        bandwidths,
        modulations,
        input_powers
    )

    for direction, frequency, bandwidth, modulation, input_power in param_combinations:
        frequency = float(frequency)
        bandwidth = int(bandwidth)
        input_power = int(input_power)

        print(f"Measuring: Direction={direction}, Freq={frequency} GHz, BW={bandwidth} MHz, Modulation={modulation}, Power={input_power} dBm")

        # Set up the RS_FSx with the current parameters
        set_center_frequency(rs_fsx, frequency)
        load_quicksave(rs_fsx)

        # Measure EVM and other parameters
        try:
            evm_points = find_evm_threshold(rs_sm, rs_fsx, config)
        except EVMMeasurementError as e:
            print(f"Measurement failed: {e}")
            continue

        # Measure additional parameters
        cf, output_power, aclr_lower, aclr_upper, eirp = measure_parameters(rs_fsx, config)

        # Collect results for this combination
        results.append({
            "direction": direction,
            "center_frequency": frequency,
            "bandwidth": bandwidth,
            "modulation": modulation,
            "input_power": input_power,
            "evm_points": evm_points,
            "cf": cf,
            "output_power": output_power,
            "aclr_lower": aclr_lower,
            "aclr_upper": aclr_upper,
            "eirp": eirp
        })

        # Save results with the generated filename
        save_measurement_results(results, frequency, bandwidth, modulation)

    return results


def save_measurement_results(results, frequency, bandwidth, modulation, directory="measurement_results"):
    """Save the measurement results to a JSON file with a dynamic filename."""
    # Create the directory if it doesn't exist
    if not os.path.exists(directory):
        os.makedirs(directory)

    # Generate the filename based on the frequency, bandwidth, and modulation
    filename = f"{directory}/results_{frequency}GHz_{bandwidth}MHz_{modulation}.json"
    
    with open(filename, 'w') as json_file:
        json.dump(results, json_file, indent=4)
    print(f"Results saved to {filename}")

