# recorder_utils.py
'''
version 1.0.0
Written by: Liew You Qing 33590400
Written on: 06/05/2025
Description: Added functions to handle the recording of audio data from the STM32 device, including manual and distance trigger modes.

version 1.0.1
Written by: Liew You Qing 33590400
Written on: 08/05/2025
Description: Completed the code to handle the conversion of raw data to WAV format and playback options.
            Added functions to handle the conversion of raw data to WAV format and playback options. 
            TODO: Add function headers and comments for clarity.
                Write a test.py to use dummy data to test the conversion and playback functions.

File Header:

'''


import serial
import matplotlib.pyplot as plt
from datetime import datetime
import subprocess
import os
import csv
import platform

# Constants
PORT = None
BAUDRATE = None
TIMEOUT = None

CHUNK_SIZE = None # Read in chunks of 500 bytes

def get_new_filename():
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    raw_filename = os.path.join("output_raw_data", f"recording_{timestamp}.data")
    wav_filename = os.path.join("output_audio", f"recorded_audio_{timestamp}.wav")
    csv_filename = os.path.join("output_raw_data_csv", f"recording_{timestamp}.csv")
    plot_filename = os.path.join("amplitude_plot", f"recording_{timestamp}.png")
    
    print(f"Generated filenames: {raw_filename}, {wav_filename}, {csv_filename}, {plot_filename}\n")
    return raw_filename, wav_filename, csv_filename, plot_filename

def send_command(ser, command):
    ser.write(command.encode())
    print(f"[>] Sent command: '{command}'")

def receiving_data(ser, binary_filename, csv_filename, plot_filename , sample_rate=10000):
    global amplitude_list
    global amplitude_time
    amplitude_time = [] # List to store amplitude values
    amplitude_list = [] # List to store time values
    sample_index = 0  # Initialize sample index

    print(f"[INFO] Receiving and saving to:\n - {binary_filename} (binary)\n - {csv_filename} (CSV)")
    bytes_read = 0

    with open(binary_filename, "ab") as bin_file, open(csv_filename, "w") as csv_file:
        writer = csv.writer(csv_file)
        
        writer.writerow(["SampleRate(Hz)", sample_rate])
        writer.writerow(["Time (s)", "Amplitude (V)"]) #header
        
        while True:
            try:
                chunk = ser.read(CHUNK_SIZE)
                if chunk:
                    bin_file.write(chunk)
                    bytes_read += len(chunk)
                    print(f"Read {len(chunk)} bytes, total: {bytes_read}\n")
                    # Extract 12-bit ADC samples (each sample = 2 bytes, little endian)
                    for i in range(0, len(chunk) - 1, 2):
                        adc_val = chunk[i] | (chunk[i + 1] << 8) # decode binary data to 12-bit ADC value manually
                        writer.writerow(adc_val) # write to CSV file
                        amplitude = adc_to_amplitude(adc_val)
                        timestamp = sample_index / sample_rate
                        amplitude_list.append(amplitude)
                        amplitude_time.append(timestamp)
                        sample_index += 1
                else:
                    print("[INFO] Timeout reached. No data received. Exiting...\n")
                    break
            except KeyboardInterrupt:
                print("[INFO] Recording interrupted by user.\n")
                break
        plot_data(amplitude_list, amplitude_time, plot_filename) # plot the data
        print(f"[INFO] Recording finished. Total bytes read: {bytes_read}\n")
        print(f"[INFO] Data saved as {binary_filename} in 'output_raw_data' folder\n")

def adc_to_amplitude(adc_val):
    return (adc_val / 4095.0) * 3.3  # 12-bit ADC

def plot_data(amplitude_list, amplitude_time, filename):
    plt.figure(figsize=(10, 5))
    plt.plot(amplitude_time, amplitude_list, label='Amplitude', color='blue')
    plt.title('ADC Amplitude over Time')
    plt.xlabel('Time (s)')
    plt.ylabel('Amplitude (V)')
    plt.grid()
    plt.legend()
    plt.savefig(filename)
    print(f"[INFO] Plot saved as {filename}\n")

def convert_to_wav(input_file, output_file):
    # Check if the file exists
    os.makedirs("output_audio", exist_ok=True)
    os.makedirs("output_raw_data", exist_ok=True)
    if not os.path.exists(input_file):
        print(f"[ERROR] Input file '{input_file}' does not exist.")
        return
    
    # teammates might use cross-platform tools, so need to check the OS
    exe = "./convert_to_wav.exe" if os.name != "nt" else "convert_to_wav.exe"

    print(f"[INFO] Running: {exe} {input_file} {output_file}")
    result = subprocess.getstatusoutput(f"{exe} {input_file} {output_file}")
    print(f"[RESULT] Exit code: {result[0]}\n")
    print(f"[RESULT] Output:\n{result[1]}\n")

    if result[0] == 0:
        print(f"[SUCCESS] WAV file saved to: {output_file}\n")
    else:
        print("[ERROR] WAV conversion failed\n")

def manual_mode(ser):
    duration = input("\nEnter recording duration in seconds (e.g., 5): \n").strip()
    if not duration.isdigit():
        print("[ERROR] Invalid input. Please enter a number.\n")
        return
    duration_sec = int(duration)
    cmd = f"manual_{duration_sec:02d}"
    send_command(ser, cmd)

    raw_file, wav_file = get_new_filename()
    receiving_data(ser, raw_file)
    convert_to_wav(raw_file, wav_file)

def distance_mode(ser):
    send_command(ser, "resume   ")
    print("[INFO] Distance trigger mode activated. Will stop if the distance is further than 10cm for 5 seconds.\n")
    print("[INFO] Or press Ctrl + C to stop recording.\n")

    raw_file, wav_file = get_new_filename()
    receiving_data(ser, raw_file)
    convert_to_wav(raw_file, wav_file)

def interrupt(ser):
    send_command(ser, "interrupt")
    
def play_audio_file(filepath):
    system = platform.system()
    try:
        if system == "Windows":
            os.startfile(filepath)
        elif system == "Linux":
            subprocess.run(["aplay", filepath])
        else:
            print("[ERROR] Unsupported OS for playback.")
    except Exception as e:
        print(f"[ERROR] Could not play audio: {e}")

    
def list_wav_files(directory="output_audio"):
    try:
        return sorted([f for f in os.listdir(directory) if f.endswith(".wav")])
    except FileNotFoundError:
        print("[ERROR] output_audio/ folder not found.")
        return []
    
def playback_menu():
    print("\n=== Playback Menu ===")
    files = list_wav_files()

    if not files:
        print("[INFO] No .wav files found in 'output_audio/'.")
        return

    for i, f in enumerate(files):
        print(f"{i + 1}. {f}")
    
    choice = input("Select a file to play (or 'q' to cancel): ").strip()
    if choice.lower() == 'q':
        return

    if choice.isdigit():
        index = int(choice) - 1
        if 0 <= index < len(files):
            filepath = os.path.join("output_audio", files[index])
            print(f"[INFO] Playing: {filepath}\n")
            play_audio_file(filepath)
        else:
            print("[ERROR] Invalid selection.")
    else:
        print("[ERROR] Invalid input.")
        


def show_menu():
    print("\n=== STM32 Audio Recorder CLI ===\n")
    print("1. Manual Recording Mode\n")
    print("2. Distance Trigger Mode\n")
    print("3. Interrupt Recording\n")
    print("4. Exit\n")
    print("5. Playback Options\n")
    return input("Select an option (1-5): \n")

def main():
    try:
        ser = serial.Serial(port=PORT, baudrate=BAUDRATE, bytesize=8, parity='N', stopbits=1, timeout=TIMEOUT)
        print(f"[INFO] Connected to {ser.name}\n")

        while True:
            choice = show_menu()
            if choice == '1':
                manual_mode(ser)
            elif choice == '2':
                distance_mode(ser)
            elif choice == '3':
                interrupt(ser)
            elif choice == '4':
                print("[INFO] Exiting CLI.\n")
                break
            elif choice == '5':
                playback_menu()
            else:
                print("[ERROR] Invalid selection. Please choose again.\n")

        ser.close()

    except serial.SerialException as e:
        print(f"[ERROR] Serial error: {e}\n")
    except KeyboardInterrupt:
        print("[ERROR] Exiting due to keyboard interrupt.\n")