# test.py

'''
File Header:

    Test script to validate the functionality of the recorder_utils module.
    This script is designed to run independently and test the functions in recorder_utils.py.
    It uses dummy data to simulate the behavior of the actual hardware.

'''

# test.py

import os
import struct
import math
from datetime import datetime
from recorder_utils import (
    adc_to_amplitude,
    convert_to_wav,
    plot_data,
    playback_menu,
    list_wav_files,
    play_audio_file,
)

def generate_dummy_adc_data(filename, num_samples=100000):
    os.makedirs("output_raw_data", exist_ok=True)
    
    import math
    print(f"[TEST] Writing {num_samples} dummy samples to {filename}")

    os.makedirs("output_audio", exist_ok=True)
    os.makedirs("output_raw_data_csv", exist_ok=True)
    os.makedirs("amplitude_plot", exist_ok=True)

    
    with open(filename, "wb") as f:
        for i in range(num_samples):
            # 12-bit sine wave (scaled to 0–4095)
            val = int((math.sin(2 * math.pi * i / 100) + 1) * 2047.5)


            # write as little-endian 2-byte (uint16)
            f.write(struct.pack('<H', val))

def generate_csv_and_plot_from_dummy(binary_file, csv_file, plot_file, sample_rate=10000):
    import csv

    print(f"[TEST] Converting {binary_file} to CSV + Plot")

    amplitude_list = []
    amplitude_time = []

    with open(binary_file, "rb") as f, open(csv_file, "w", newline='') as csvfile:
        writer = csv.writer(csvfile)
        writer.writerow([sample_rate])

        index = 0
        while True:
            two_bytes = f.read(2)
            if len(two_bytes) < 2:
                break
            adc_val = struct.unpack('<H', two_bytes)[0]
            amplitude = (adc_val / 4095.0) * 3.3
            time_sec = index / sample_rate
            writer.writerow([time_sec, amplitude])
            amplitude_list.append(amplitude)
            amplitude_time.append(time_sec)
            index += 1

    plot_data(amplitude_list, amplitude_time, plot_file)

def full_test():
    """Run the complete test."""
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    binary_file = os.path.join("output_raw_data", f"test_{timestamp}.data")
    csv_file = os.path.join("output_raw_data_csv", f"test_{timestamp}.csv")
    wav_file = os.path.join("output_audio", f"test_{timestamp}.wav")
    plot_file = os.path.join("amplitude_plot", f"test_{timestamp}.png")

    print(f"\n[TEST] Creating dummy ADC file: {binary_file}")
    generate_dummy_adc_data(binary_file, num_samples=10000)

    print(f"[TEST] Generating CSV and Plot...")
    generate_csv_and_plot_from_dummy(binary_file, csv_file, plot_file)

    print(f"[TEST] Converting to WAV: {wav_file}")
    convert_to_wav(binary_file, wav_file)

    if os.path.exists(wav_file):
        print("\n[TEST] WAV file ready for playback.\n")

    print("[TEST] Test complete.\n")
    print(f"[FILES GENERATED]\n - Binary: {binary_file}\n - CSV: {csv_file}\n - Plot: {plot_file}\n - WAV: {wav_file}\n")

    playback_menu()

if __name__ == "__main__":
    import csv
    full_test()