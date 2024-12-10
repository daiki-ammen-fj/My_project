import time
from logging import getLogger, INFO, StreamHandler
from instrument_lib import RS_FSx  # Import the instrument driver

def connect_signal_analyzer(ip_address: str, password: str, FSWP: bool = False) -> None:
    """Connects to the Signal Analyzer and retrieves measurement data."""
    
    # Setup logger for displaying information
    logger = getLogger()
    logger.setLevel(INFO)
    logger.addHandler(StreamHandler())

    # Connect to the RS_FSx Spectrum Analyzer
    print(f"Connecting to RS_SMx Spectrum Analyzer at IP: {ip_address}...")
    sa = RS_FSx(ip_address=ip_address)

    # Connect to the device
    sa.connect()
    logger.info(f"Connected. Device info: {sa.identification}")

    # Get and display the device name
    id_ = sa.get_name()
    logger.info(f"Device Name: {id_}")

    # Standard mode operation
    if not FSWP:
        print("Running in standard mode...")

        # Set and verify frequency
        target_freq = 3e9  # 3 GHz
        print(f"Setting frequency to {target_freq / 1e9} GHz...")
        sa.set_freq(target_freq)
        freq = sa.get_freq()
        logger.info(f"Frequency: {freq} Hz")
        assert freq == target_freq, "Frequency mismatch!"

        # Get peak amplitude and frequency
        peak_amp, peak_freq = sa.get_peak()
        logger.info(f"Peak Amplitude: {peak_amp} dBm")
        logger.info(f"Peak Frequency: {peak_freq} Hz")

        # Get frontend temperature
        temp = sa.get_frontend_temp()
        logger.info(f"Frontend Sensor Temperature: {temp} °C")

    # FSWP mode operation
    elif FSWP:
        print("Running in FSWP mode...")

        # Run LO startup process
        sa.run_lo_startup(with_x4=False)

        # Get and display the device name
        id_ = sa.get_name()
        logger.info(f"Device Name: {id_}")

        # Get the single measurement runtime
        single_measurement_time = sa.get_single_time_fswp()

        # Run a single measurement and wait for completion
        sa.run_single_fswp()
        time.sleep(single_measurement_time)

        # Retrieve jitter measurements
        j1, j2, j3 = sa.get_jitter_fswp(1), sa.get_jitter_fswp(2), sa.get_jitter_fswp(3)

        # Retrieve integrated noise measurements
        n1, n2, n3 = sa.get_int_noise_fswp(1), sa.get_int_noise_fswp(2), sa.get_int_noise_fswp(3)

        # Retrieve spot noise measurements
        s1, s2, s3 = sa.get_spot_noise_fswp(1), sa.get_spot_noise_fswp(2), sa.get_spot_noise_fswp(3)
        s4, s5, s6 = sa.get_spot_noise_fswp(4), sa.get_spot_noise_fswp(5), sa.get_spot_noise_fswp(6)

        # Retrieve power and frequency
        power = sa.get_power_fswp()
        freq = sa.get_freq_fswp()

        # Retrieve frontend temperature
        temp = sa.get_frontend_temp()

        # Log results
        logger.info(f"Center Frequency: {freq} Hz")
        logger.info(f"Signal Level: {power} dBm")
        logger.info(f"Jitter: {j1}, {j2}, {j3}")
        logger.info(f"Integrated Noise: {n1}, {n2}, {n3}")
        logger.info(f"Spot Noise: {s1}, {s2}, {s3}, {s4}, {s5}, {s6}")
        logger.info(f"Single Measurement Runtime: {single_measurement_time} s")
        logger.info(f"Frontend Sensor Temperature: {temp} °C")

    # Close connection
    print("Closing connection...")
    sa.close()

