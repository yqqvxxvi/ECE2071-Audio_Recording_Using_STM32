# ECE2071-Audio_Recording  
**Using STM32 + Python CLI**

---

## 📝 Overview

This project implements a complete **audio recording and processing system** using two STM32 microcontrollers and a Python-based CLI on a PC. It supports **manual** and **distance-triggered recording**, processes raw ADC data sent via UART, converts it into a playable `.wav` file, and generates visual plots of amplitude over time.

---

## 🛠️ System Architecture

- **Two STM32 boards**:
  - One acts as the **main recorder**, sampling audio using a 12-bit ADC.
  - The other acts as a **bridge/trigger controller**.
- **Inter-STM32 communication**: via **SPI**
- **STM32 to PC** communication: via **UART2**
- **Host PC** runs a Python CLI tool (`recorder_utils.py`) to:
  - Send control commands
  - Receive binary audio data
  - Save, process, and visualize the recording

---

## 🎯 STM32 Operation Modes

- `manual_XX` — Records audio for **XX seconds**  
- `resume` — Starts **distance-triggered** recording (<10cm detected by ultrasonic sensor)  
- `interrupt` — Immediately stops any recording  
- LED indicators are used for feedback (e.g., recording active, user detected)

---

## 📦 Features

- 🖥️ Menu-driven Python CLI
- 🎙️ Manual and ultrasonic-based trigger modes
- 🧲 Inter-STM32 SPI communication
- 📤 UART data streaming to PC
- 📂 Files generated per session:
  - `.data` — Raw 12-bit ADC samples (binary)
  - `.csv` — Time vs amplitude logs
  - `.png` — Amplitude-time plot
  - `.wav` — Converted audio
- 🔊 Playback interface for `.wav` files
- 🧪 `test.py` simulates the entire pipeline with dummy ADC data

---

## 📁 Folder Structure
.
├── recorder_utils.py # CLI with UART control, data saving, and playback
├── test.py # Test script with dummy data (no STM32 needed)
├── convert_to_wav.exe # C-based executable to convert .data → .wav
├── output_raw_data/ # Binary recordings
├── output_raw_data_csv/ # CSVs (timestamp + amplitude)
├── output_audio/ # Converted .wav files
├── amplitude_plot/ # Amplitude vs time plots (.png)
.
---

## 🚀 How to Use

### 1. Start the CLI

python ./recorder.py

### 2. Choose an option from the menu:

=== STM32 Audio Recorder CLI ===
1. Manual Recording Mode
2. Distance Trigger Mode
3. Interrupt Recording
4. Exit
5. Playback Options

#### Mode Details
- Manual Mode
Records for a specified number of seconds (e.g., manual_05 = 5s)

- Distance Trigger Mode
Continuously records while a user is detected <10cm. Stops after 5s of no presence.

- Interrupt Mode
Instantly halts any recording.

- Playback
Browse and play .wav files saved in output_audio/.

## Test the Full Pipeline (No STM32 Required)

You can run a dummy test to verify all functionality:

python test.py

This will:

- Generate synthetic .data file with sine wave values

- Create .csv and .png

- Convert to .wav via convert_to_wav.exe

- Launch playback menu


## Author
Liew You Qing
Student ID: 33590400
Monash University
Course: ECE2071 Systems Programming — Semester 1, 2025
