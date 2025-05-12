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

version 1.0.2
Written by: Naamjas Singh 34392017
Written on: 09/05/2025
Description: Added function headers to explain functions
            Edited playback_menu function to continously show menu after playing song until user quit
            Edited show_menu function to display error message for wrong input
            TODO: make distance for distance_mode a custom input from user 
            (send byte of distance to be used and tell processing stm to stop sending data via loop when user outside range)

File Header:
            Main file and CLI that user interacts with. Functions are called within this file and outputs (graphs + audios etc) are outputted from this file. 
'''
#import modules to be used
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

'''
Generates unique filenames based on timestamp (second, minute, hour, day, month, year) for raw data, recorded audio, csv and plot file. 

Parameters: 
None

Returns: 
Tuple containing generated filenames.

Note: 
Tuples were used since they cannot be edited once created, thus it is secure and can't be modified or corrupted

Example usage:
    filenames = get_new_filename()
    raw_filename, wav_filename, csv_filename, plot_filename = filenames
'''
def get_new_filename():
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    raw_filename = os.path.join("output_raw_data", f"recording_{timestamp}.data")
    wav_filename = os.path.join("output_audio", f"recorded_audio_{timestamp}.wav")
    csv_filename = os.path.join("output_raw_data_csv", f"recording_{timestamp}.csv")
    plot_filename = os.path.join("amplitude_plot", f"recording_{timestamp}.png")
    
    print(f"Generated filenames: {raw_filename}, {wav_filename}, {csv_filename}, {plot_filename}\n")
    return raw_filename, wav_filename, csv_filename, plot_filename

'''
Encodes data into bytes and writes data to serial device via serial port

Parameters:
ser = serial port connected to device, command = command to be sent

Returns: 
None

Note: 
Assumes ser is alrdy set to ser = serial.Serial("COM_", XXXX) for the respective port and baudrate used

Example usage:
    send_command(ser, "START")
'''
def send_command(ser, command):
    ser.write(command.encode())
    print(f"[>] Sent command: '{command}'")

'''
Function takes in filenames and writes data to list of equal sizes. Saves file as binary, csv, and plot files.

Parameters: 
ser = serial port connected to device, command = command to be sent
binary_filename = filename to save raw binary audio data  
csv_filename = filename to save time-amplitude data in CSV format  
plot_filename = filename to save amplitude-time plot as image  
sample_rate = sample rate of ADC recording (default: 10000 Hz)

Returns: 
None

Note:


Example usage:
    receiving_data(ser, "audio_01.bin", "audio_01.csv", "audio_01.png")
'''
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
        
        #process serial data
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

'''
Converts adc values into voltage values that can be read by STM and to be used for amplitude plotting 

Parameters: 
Adc integer values between 0 and 4095 

Returns: 
Voltage value of type float between 0 and 3.3

Note: 
3.3V is used as the reference voltage since the STM32 reads 3.3V as the max voltage

Example usage:
    adc_to_ampltitude(2048) #returns 1.650
'''
def adc_to_amplitude(adc_val):
    return (adc_val / 4095.0) * 3.3  # 12-bit ADC

'''
Plots data obtained into a graph of Amplitude against Time and saves it as a png file

Parameters: 
Amplitude_list = list of float values, amplitude_time = float time values in seconds, filename = file to to write data to

Returns: 
None

Note: 
Assume amplitude_list and amplitude_time are same length. File is saved using savefig but not shown on screen using plt.show

Example usage:
    plot_data(amplitudes, time_lsit, 'amplitude_time.png')
'''
def plot_data(amplitude_list, amplitude_time, filename):
    plt.figure(figsize=(10, 5)) # sets width and height of figure
    plt.plot(amplitude_time, amplitude_list, label='Amplitude', color='blue')
    plt.title('ADC Amplitude over Time')
    plt.xlabel('Time (s)')
    plt.ylabel('Amplitude (V)')
    plt.grid() 
    plt.legend()
    plt.savefig(filename)
    print(f"[INFO] Plot saved as {filename}\n")

'''
Function converts binary audio input file and writes it to an output wav. file

Parameters: 
inpu_file (str) : Path to data file 
output_file (str) : Path to output file to write to 

Returns: 
None. Prints success or error message to terminal.

Note: 
Creates directory folder if missing. Type of error not displayed

Example usage:
        convert_to_wav("recording_20250509_120000.data", recorded_audio_20250509_120000.wav")
'''
def convert_to_wav(input_file, output_file):

    #Check if file exists. exist_ok does not raise error if alrdy exists. 
    os.makedirs("output_audio", exist_ok=True)
    os.makedirs("output_raw_data", exist_ok=True)
    if not os.path.exists(input_file):
        print(f"[ERROR] Input file '{input_file}' does not exist.")
        return
    
    # teammates might use cross-platform tools, so need to check the OS. nt for Windows. 
    exe = "./convert_to_wav.exe" if os.name != "nt" else "convert_to_wav.exe"

    print(f"[INFO] Running: {exe} {input_file} {output_file}")
    result = subprocess.getstatusoutput(f"{exe} {input_file} {output_file}")
    print(f"[RESULT] Exit code: {result[0]}\n")
    print(f"[RESULT] Output:\n{result[1]}\n")

    #check tuple from result above. 
    if result[0] == 0:
        print(f"[SUCCESS] WAV file saved to: {output_file}\n")
    else:
        print("[ERROR] WAV conversion failed\n")

'''
Custom user-set duration to record audio in seconds. Processes incoming audio and saves data into raw & wav files.

Parameters: 
ser = serial port connected to device, user inputs time in int type

Returns: 
None. If invalidate user input, returns error message

Note: 
Asumes ser is alrdy set to ser = serial.Serial("COM_", XXXX) for the respective port and baudrate used

Example usage:
    manual_mode(ser)
    Enter recording duration in seconds (e.g., 5):
    10
'''
def manual_mode(ser):
    duration = input("\nEnter recording duration in seconds (e.g., 5): \n").strip()
    if not duration.isdigit(): #check for only digits, otherwise return error
        print("[ERROR] Invalid input. Please enter a number.\n")
        return
    duration_sec = int(duration)
    cmd = f"manual_{duration_sec:02d}"  #format as 2 digit integer
    send_command(ser, cmd)  #send to STM

    #call other functions
    raw_file, wav_file, _, _ = get_new_filename()  #func returns 4 filenames but only need 2
    receiving_data(ser, raw_file)
    convert_to_wav(raw_file, wav_file)

'''
Function sends command of when to record and which mode (distance mode). Displays menu to user. Saves audio input as raw & wav files. 

Parameters: 
ser = serial port connected to device

Returns: 
None. 

Note: 
Asumes ser is alrdy set to ser = serial.Serial("COM_", XXXX) for the respective port and baudrate used

Example usage:
    distance_mode(ser)
    [INFO] Distance trigger mode activated. Will stop if the distance is further than 10cm for 5 seconds.
    [INFO] Or press Ctrl + C to stop recording.
'''
def distance_mode(ser):
    send_command(ser, "resume   ")
    print("[INFO] Distance trigger mode activated. Will stop if the distance is further than 10cm for 5 seconds.\n")
    print("[INFO] Or press Ctrl + C to stop recording.\n")

    #function calls to save data
    raw_file, wav_file, _, _ = get_new_filename()
    receiving_data(ser, raw_file)
    convert_to_wav(raw_file, wav_file)

'''
Function sends interrupt message to STM

Parameters: 
ser = serial port connected to device

Returns: 
None. 

Note: 
Asumes ser is alrdy set to ser = serial.Serial("COM_", XXXX) for the respective port and baudrate used

Example usage:
    interrupt(ser)
'''
def interrupt(ser):
    send_command(ser, "interrupt")

'''
Function runs the specified audio file

Parameters: 
Filepath of audio file to be played

Returns: 
None. 

Note: 
Supports Windows and Linux. Prints error for other operating systems.

Example usage:
    play_audio_file("recorded_audio_20250509_103000.wav")
'''
def play_audio_file(filepath):
    system = platform.system()
    #for teammates using different OS
    try:
        if system == "Windows":
            os.startfile(filepath)  #use default player
        elif system == "Linux":
            subprocess.run(["aplay", filepath])  #command line audio file player
        else:
            print("[ERROR] Unsupported OS for playback.")
    except Exception as e:      #saves error message in variable e
        print(f"[ERROR] Could not play audio: {e}")     #prints error message + actual error message 

'''
Function sorts and lists the wav files available.

Parameters: 
Directory to search for audio files

Returns: 
Sorted list of audio files available. If error is found, returns folder not found. 

Note: 
Only displays wav files. 

Example usage:
    audio_files = list_wav_files()
'''
def list_wav_files(directory="output_audio"):
    try:
        return sorted([f for f in os.listdir(directory) if f.endswith(".wav")]) #dispay all wav. files sorted alphabetically
    except FileNotFoundError:
        print("[ERROR] output_audio/ folder not found.")
        return []

'''
Function continously shows menu for user to pick wav. file to play until user quits

Parameters: 
User input "q" to quit or integer to play listed file. 

Returns: 
Plays specified wav file. Returns if user quits via "q"
Returns error message if invalid selection or no wav. files. 

Note: 
Available files are numbered for user to select. Function restarts after playing wav. file

Example usage:
    playback_menu()
'''
def playback_menu():
    #continously show menu after playing audio file
    while True:
        print("\n=== Playback Menu ===")
        files = list_wav_files()
            
        if not files:
            print("[INFO] No .wav files found in 'output_audio/'.")
            return

        for i, f in enumerate(files):   #prints numbered list
            print(f"{i + 1}. {f}")
        
        choice = input("Select a file to play (or 'q' to cancel): ").strip()
        if choice.lower() == 'q':
            print('[INFO] Exiting playback menu')
            break #exit loop and quit function

        if choice.isdigit():
            index = int(choice) - 1
            if 0 <= index < len(files): #error check if integer entered exceeds list size
                filepath = os.path.join("output_audio", files[index])
                print(f"[INFO] Playing: {filepath}\n")
                play_audio_file(filepath)
            else:
                print("[ERROR] Invalid selection.")
        else:
            print("[ERROR] Invalid input.")
        
'''
Function prints menu for user in the terminal and returns the listed selection number.

Parameters: 
User inputs integer between 1-5 to select option

Returns: 
Integer from 1-5 of which option the user selected. 
Returns error is input exceeds list range or is not an integer

Note: 
Function catches error from user input. 

Example usage:
    show_menu()
'''
def show_menu():
    print("\n=== STM32 Audio Recorder CLI ===\n")
    print("1. Manual Recording Mode\n")
    print("2. Distance Trigger Mode\n")
    print("3. Interrupt Recording\n")
    print("4. Exit\n")
    print("5. Playback Options\n")
    selection = input("Select an option (1-5): \n")
    try: 
        selection_d = int(selection)
        if 1 <= selection_d <= 5:
            return selection_d
        else:
            print("[ERROR] Only input a number from 1-5")
    except ValueError: 
        print("[ERROR] Invalid input.\nOnly input a number from 1-5")


def main():
    try:
        #initialise serial port
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
        ser.close()

    #check for error when closing serial port
    except serial.SerialException as e:
        print(f"[ERROR] Serial error: {e}\n")
    except KeyboardInterrupt:
        print("[ERROR] Exiting due to keyboard interrupt.\n")
