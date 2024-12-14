#!python3.11
# step4_run_paam.py

import os
import sys
import subprocess
import logging

def run_paam_script(script_path):
    """Step 4: Run PAAM download script if the path is valid."""
    try:
        # Get the absolute path of the batch file
        batch_dir = os.path.dirname(os.path.abspath(script_path))
        
        # Log the absolute path for debugging
        logging.info(f"Checking directory: {batch_dir}")
        
        # Check if the directory exists
        if os.path.exists(batch_dir) and os.path.isdir(batch_dir):
            logging.info(f"Directory exists: {batch_dir}")
        else:
            logging.error(f"Directory {batch_dir} not found. Exiting program.")
            sys.exit(1)  # Exit the program if the directory is not found

        # Check if the batch file exists in the directory
        if os.path.isfile(script_path):
            logging.info(f"Batch script found: {script_path}")
        else:
            logging.error(f"Batch script not found: {script_path}. Exiting program.")
            sys.exit(1)  # Exit the program if the batch file is not found

        # If the batch file exists, execute it
        logging.info(f"Executing PAAM batch script: {script_path}")
        subprocess.run([script_path], shell=True, check=True)
        
    except subprocess.CalledProcessError as e:
        # Handle errors during batch script execution
        logging.error(f"Error during PAAM script execution: {e}")
        sys.exit(1)  # Exit if script execution fails
    
    except Exception as e:
        # Handle any unexpected errors
        logging.error(f"An unexpected error occurred: {e}")
        sys.exit(1)  # Exit the program if an unexpected error occurs
