#!python3.11
# plot_measurements.py

import json
import matplotlib.pyplot as plt

def load_json_data(filename):
    """Load the measurement results from a JSON file."""
    with open(filename, 'r') as file:
        data = json.load(file)
    return data

def plot_evm_vs_eirp(data):
    """Plot EVM vs EIRP from the loaded data."""
    # Extract EVM and EIRP values
    evm_values = [entry["evm"] for entry in data]
    eirp_values = [entry["eirp"] for entry in data]

    # Create the plot
    plt.figure(figsize=(10, 6))
    plt.plot(eirp_values, evm_values, marker='o', linestyle='-', color='b', label='EVM vs EIRP')
    plt.xlabel('EIRP (dBm)')
    plt.ylabel('EVM (%)')
    plt.title('EVM vs EIRP')
    plt.grid(True)
    plt.legend()
    plt.show()

def main():
    # Specify the path to the JSON file
    filename = "results/measurement_results.json"
    
    # Load the data from the JSON file
    data = load_json_data(filename)
    
    # Plot EVM vs EIRP
    plot_evm_vs_eirp(data)

if __name__ == "__main__":
    main()
