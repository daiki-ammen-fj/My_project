#!python3.11
# step2_run_batch.py

import subprocess

def run_batch_script(script_path):
    print("Step 2: Running batch script...")
    try:
        subprocess.run([script_path], shell=True, check=True)
    except subprocess.CalledProcessError as e:
        print(f"Failed to run batch script: {e}")
        raise
