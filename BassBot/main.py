import os
import time
import threading
from collections import deque
from datetime import datetime
import concurrent.futures

from bass import Bass
from config import *
from relay import Relay
from servo import ServoController
from gpiozero.pins.pigpio import PiGPIOFactory
import board
import adafruit_ina260
from time import sleep
from gpiozero import Servo
from currentLogging import*
from currentLogging import start_logging_multirate, stop_logging

# Ensure LogFiles directory exists
log_dir = "LogFiles"
os.makedirs(log_dir, exist_ok=True)

# Create timestamped filename in the directory
timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
filename = os.path.join(log_dir, f"ina260_multirate_{timestamp}.csv")

# Initialize components
bass = Bass()
fret_current_stream = deque(maxlen=20)

# Start logging
threads, file_handle = start_logging_multirate(filename, fret_current_stream)

def multi_pick(servo, current_stream, times=3, threshold=2000, delay_after_pick=0.3):
    for i in range(times):
        print(f"[MultiPick] Waiting for spike {i+1}/{times}")
        servo.pickWithDamp(current_stream, threshold)
        print(f"[MultiPick] Pick {i+1} complete")
        time.sleep(delay_after_pick)

def motion_sequence():
    while True:
        print("[Motion] Starting step...")
        bass.fret4.on()
        
        with concurrent.futures.ThreadPoolExecutor() as executor:
            future = executor.submit(multi_pick, bass.servoD, fret_current_stream, 6, 3000)
            future.result()

        print("[Motion] All picks complete. Turning off fret.")
        bass.fret4.off()
        time.sleep(4)

# Run motion sequence in its own thread so live plot etc. continues
motion_thread = threading.Thread(target=motion_sequence, daemon=True)
motion_thread.start()

try:
    while True:
        time.sleep(0.5)
except KeyboardInterrupt:
    print("Interrupted by user.")
finally:
    stop_logging(threads, file_handle)
    bass.cleanup()
    print(f"Data saved to {filename}")
    print("Exited cleanly.")
