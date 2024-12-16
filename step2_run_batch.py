#!python3.11
# step2_run_batch.py

import os
import sys
import logging

def run_batch_script(script_path):
    """Step 2: Run batch script if the path is valid."""
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

        # If the batch file exists, execute it (uncomment to execute)
        logging.info(f"Executing batch script: {script_path}")
        # Uncomment the next line to actually execute the batch script
        os.system(script_path)  # Using os.system for simplicity. You can replace with subprocess if needed.
        
    except Exception as e:
        # Handle any unexpected errors
        logging.error(f"An unexpected error occurred: {e}")
        sys.exit(1)  # Exit the program if an unexpected error occurs
