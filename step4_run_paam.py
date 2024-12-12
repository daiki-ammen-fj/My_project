#!python3.11
# step4_run_paam.py

import subprocess

def run_paam_script(script_path):
    print(f"Step 4: Running PAAM download script at {script_path}...")
    try:
        subprocess.run([script_path], shell=True, check=True)
    except subprocess.CalledProcessError as e:
        print(f"Failed to run PAAM script: {e}")
        raise
