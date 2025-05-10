# recorder.py
'''
version 1.0.0
Written by: Liew You Qing 33590400
Written on: 08/05/2025


File Header:

    Main script to run the data recorder for the ADC device.

'''

import serial
import matplotlib.pyplot as plt
import time
from datetime import datetime
import subprocess
import recorder_utils

# Constants
recorder_utils.PORT = 'COM5'
recorder_utils.BAUDRATE = 230400
recorder_utils.TIMEOUT = 5
recorder_utils.CHUNK_SIZE = 500  # Read in chunks of 500 bytes

# # Set the FILENAME globally for use in recorder_utils
# FILENAME = f"recording_{datetime.now().strftime('%Y%m%d_%H%M%S')}.data"
# recorder_utils.FILENAME = FILENAME

        
if __name__ == "__main__":
    recorder_utils.main()
    
