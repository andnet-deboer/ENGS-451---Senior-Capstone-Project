#READ THIS! to run this code first run the command below:
#sudo pigpiod
from gpiozero import Servo
import lib8relind
from gpiozero.pins.pigpio import PiGPIOFactory
from time import sleep
import time
import os
import numpy as np
import lib8relind
import RPi.GPIO as GPIO
import atexit
from music21 import *
import time
import time
import board
import adafruit_ina260
import threading
import matplotlib.pyplot as plt
from matplotlib.animation import FuncAnimation
from collections import deque



# Import necessary libraries
#from music21 import *
import time
from datetime import datetime
import concurrent.futures

#  Servo Motor connnectios #
"               E    A     D    G"
" Fret 1        |    |     |    |   "
" Fret 2        |    |     |    |   "
" Fret 3        |    |     |    |   "
" Fret 4        |    |     |    |   "
"              24   18    27   10   "

factory = PiGPIOFactory()
initial_value = 0

# servoG = Servo(10, pin_factory=factory, initial_value=initial_value)
# servoD = Servo(27, pin_factory=factory, initial_value=initial_value)
# servoA = Servo(18, pin_factory=factory, initial_value=initial_value)
# servoE = Servo(24, pin_factory=factory, initial_value=initial_value)

#fret1 =  Relay(4)
# Variables
bpm        =  60    # beats per minute
low_angle  = -45    # min -90 degrees
high_angle = -5    # max  90 degrees
increment  = 0.05
start_time = time.time()

class CurrentSensor:
    def __init__(self,address):
        self.i2c = board.I2C()  # uses board.SCL and board.SDA
        # i2c = board.STEMMA_I2C()  # For using the built-in STEMMA QT connector on a microcontroller
        self.ina260 = adafruit_ina260.INA260(self.i2c,address=address)
        # Initialize lists to store data
        self.times = []
        self.currents = []
        self.voltages = []

    def current(self):
        return self.ina260.current
    
    def voltage(self):
        return self.ina260.voltage
    
    def power(self):
        return self.ina260.voltage



class Relay:
    def __init__(self, relay_number):
        self.relay_number = relay_number
        
    def on(self):
        relay = self.relay_number
        if (relay == 6):
            relay = 7
        elif (relay == 7):
            relay = 6
        lib8relind.set(0, relay, 1)

    def off(self):
        relay = self.relay_number
        if (relay == 6):
            relay = 7
        elif (relay == 7):
            relay = 6
        lib8relind.set(0, relay, 0)
        
    def get(self):
        return lib8relind.get(0, self.relay_number)
    


def count(count, bpm, servo, low_angle=-45, high_angle=-5): 
    cnt = 0
    while count >= cnt:
        servo.value = low_angle / 90
        sleep(60 / (0.95*bpm))
        cnt +=1            
        servo.value = high_angle / 90
        sleep(60 / (0.95*bpm))
        cnt += 1

#Then initialize your servos like this:
#Then initialize your servos like this:
fret1 = Relay(3)
fret2 = Relay(1)
fret3 = Relay(4)
fret4 = Relay(2)
damper = Relay(5)

def relay_off(except_fret=None):
    if except_fret != fret1:
        fret1.off()
    if except_fret != fret2:
        fret2.off()
    if except_fret != fret3:
        fret3.off()
    if except_fret != fret4:
        fret4.off()

class ServoController:
    def __init__(self, pin, factory=factory, initial_value=0, name=None, LOW=-30, HIGH=30, offset=0):
        self.name = name
        self.pin = pin
        self.state = True
        self.servo = Servo(pin, pin_factory=factory, initial_value=initial_value)
        self.low = LOW
        self.high= HIGH
        self.offset=offset
        
    def set_angle(self, angle):
        # Convert angle (-90 to 90) to value (-1 to 1)
        self.servo.value = angle / 90
        
    def count(self, count, bpm, low_angle=-45, high_angle=-5):
        cnt = 0
        while count >= cnt:
            self.set_angle(low_angle)
            sleep(60 / (1.0*bpm))
            cnt += 1
            self.set_angle(high_angle)
            sleep(60 / (1.0*bpm))
            cnt += 1

    ''''
    PICK A STRING
    @param state (low=0) (high=1)
    @param low   (low angle)
    @param high  (high angle)
    '''
    def pick(self):
        if (self.state):
            self.set_angle(self.low)
            self.state = False
        else:
            self.set_angle(self.high)
            self.state = True

    def pickWithDamp(self, current_stream, threshold=2000, timeout=2.0, poll_interval=0.01):
        start = time.time()
        while (time.time() - start) < timeout:
            if len(current_stream) >= 2:
                recent_values = list(current_stream)[-2:]
                if any(c > threshold for c in recent_values):
                    print(f"[{self.name}] Spike detected, picking")
                    if self.state:
                        self.set_angle(self.low)
                        self.state = False
                    else:
                        self.set_angle(self.high)
                        self.state = True
                    return
            time.sleep(poll_interval)
        print(f"[{self.name} WARNING] No spike detected in {timeout}s.")

      
    def detach(self):
        self.servo.detach()
        
    def zero(self):
        self.servo.value = 0
        
    def on(self):
        self.servo.value = 1

#Then initialize your servos like this:
servoG = ServoController(10, name='G')
servoD = ServoController(27, name='D')
servoA = ServoController(18, name='A')
servoE = ServoController(24, name='E')

def detach_servos(except_servo=None):
    if except_servo != servoG:
        servoG.detach()
    if except_servo != servoD:
        servoD.detach()
    if except_servo != servoA:
        servoA.detach()
    if except_servo != servoE:
        servoE.detach()

''' A function that turns off Relays on exit '''
def detach_relays():
    lib8relind.set_all(0,0)
''' Set all servos to zero position '''
def zero_servos():
    servoG.value = 0
    servoD.value = 0
    servoA.value = 0
    servoE.value = 0

    ''' Set all servos to zero position '''
def on_servos():
    servoG.value = 1
    servoD.value = 1
    servoA.value = 1
    servoE.value = 1

atexit.register(detach_servos)



def cleanup():
    detach_servos()
    detach_relays()
    GPIO.cleanup()

def run_servo(servo):
    count(-1, bpm, servo)
# Define the dictionary mapping notes to servos
note_servo_oct2 = {
    'E': [servoE,0],
    'F': [servoE,fret1],
    'F#':[servoE,fret2],
    'G': [servoE,fret3],
    'G#':[servoE,fret4],
    'A': [servoA,0],
    'A#': [servoA,fret1],
    'B': [servoA,fret2]
    #One optio
}
note_servo_oct3 = {
    'C': [servoA,fret3],
    'C#': [servoA,fret4],
    'D': [servoD,0],
    'D#': [servoD,fret1],
    'E': [servoD,fret2],
    'F': [servoD,fret3],
    'F#': [servoD,fret4],
    'G': [servoG,0],
    'G#': [servoG,fret1],
    'A': [servoG,fret2],
    'A#':[servoG,fret3],
    'B': [servoG,fret4]
}

''' Play notes with increasing tempo'''
def acceleratedBPM(startBpm=60, maxBpm=140, step=40, strokes=5, servo=servoA, servo2=servoG):
    for i in range(startBpm, maxBpm, step):
        print(f"Current BPM: {i}")
        print(f"Current Stroke: {strokes}")
        print(f"Current Servo: {servo}")
        count(strokes, i, servo, low_angle=LOW, high_angle=HIGH)
        count(strokes, i, servo2, low_angle=LOW, high_angle=HIGH)

def chromaticScale(delay=0.6,LOW=-30, HIGH=30):
        time.sleep(delay/2)
        fret1.on()
        time.sleep(delay/5)
        servoE.pick(LOW,HIGH)
        print("ServoE")
        time.sleep(delay)
        fret1.off()
        
        time.sleep(delay/2)
        fret2.on()
        time.sleep(delay/2)
        servoA.pick(LOW,HIGH)
        print("ServoA")
        time.sleep(delay)
        fret2.off()

        time.sleep(delay/2)
        fret3.on()
        time.sleep(delay/2)
        servoD.pick(LOW,HIGH)
        print("ServoD")
        time.sleep(delay)
        fret3.off()

        time.sleep(delay/2)
        fret4.on()
        time.sleep(delay/2)
        servoG.pick(LOW,HIGH)
        print("ServoG")
        time.sleep(delay)
        fret4.off()

def log_sensor_values(sensor, label, rate, start_time, data_dict, data_lock, current_stream=None):
    period = 1.0 / rate
    while logging_active:
        loop_start = time.time()
        try:
            t = loop_start - start_time
            current = sensor.current()
            voltage = sensor.voltage()

            with data_lock:
                data_dict[label] = (t, current, voltage)
            if current_stream is not None:
                current_stream.append(current)
        except Exception as e:
            print(f"[{label} ERROR] {e}")

        elapsed = time.time() - loop_start
        sleep_time = period - elapsed
        if sleep_time > 0:
            time.sleep(sleep_time)



def start_logging_multirate(filename="ina260_multicolumn.csv"):
    fret_sensor = CurrentSensor(0x44)
    damper_sensor = CurrentSensor(0x41)
    servo_sensor = CurrentSensor(0x40)

    global logging_active
    logging_active = True
    start = time.time()

    data_lock = threading.Lock()
    sensor_data = {}

    file_handle = open(filename, "w")
    file_handle.write("Time(s),Fret_Current(mA),Fret_Voltage(V),Damper_Current(mA),Damper_Voltage(V),Pick_Current(mA),Pick_Voltage(V)\n")

    def csv_writer():
        while logging_active:
            with data_lock:
                fret = sensor_data.get("FRET", (None, None, None))
                damper = sensor_data.get("DAMPER", (None, None, None))
                pick = sensor_data.get("PICK", (None, None, None))
                t = time.time() - start
                line = f"{t:.3f}," \
                       f"{fret[1] if fret[1] else ''},{fret[2] if fret[2] else ''}," \
                       f"{damper[1] if damper[1] else ''},{damper[2] if damper[2] else ''}," \
                       f"{pick[1] if pick[1] else ''},{pick[2] if pick[2] else ''}\n"
                file_handle.write(line)
                file_handle.flush()
            time.sleep(0.01)  # log at ~100Hz to capture updates from any sensor

    threads = [
        threading.Thread(target=log_sensor_values, args=(fret_sensor, "FRET", 100, start, sensor_data, data_lock, fret_current_stream)),
        threading.Thread(target=log_sensor_values, args=(damper_sensor, "DAMPER", 100, start, sensor_data, data_lock)),
        threading.Thread(target=log_sensor_values, args=(servo_sensor, "PICK", 20, start, sensor_data, data_lock)),
        threading.Thread(target=csv_writer)
    ]

    for t in threads:
        t.start()

    return threads, file_handle

def stop_logging(threads, file_handle):
    global logging_active
    logging_active = False
    for t in threads:
        t.join()
    file_handle.close()
    print("Logging stopped and file saved.")


def live_plot_multirate(window_duration=10, interval=50):
    """
    Live plot of current readings for FRET, DAMPER, and PICK sensors.
    
    :param window_duration: seconds to show in the sliding window
    :param interval: update interval in milliseconds
    """
    fret_sensor = CurrentSensor(0x44)
    damper_sensor = CurrentSensor(0x41)
    pick_sensor = CurrentSensor(0x40)

    # Data storage
    time_vals = deque()
    fret_vals = deque()
    damper_vals = deque()
    pick_vals = deque()

    start = time.time()

    # Setup plot
    fig, ax = plt.subplots()
    line_fret, = ax.plot([], [], label='FRET', lw=2)
    line_damper, = ax.plot([], [], label='DAMPER', lw=2)
    line_pick, = ax.plot([], [], label='PICK', lw=2)

    ax.set_ylim(0, 6000)  # Adjust as needed
    ax.set_title("Live Current Readings (INA260)")
    ax.set_xlabel("Time (s)")
    ax.set_ylabel("Current (mA)")
    ax.legend(loc="upper right")
    ax.grid(True)

    def update(frame):
        now = time.time() - start
        try:
            fret = fret_sensor.current()
            damper = damper_sensor.current()
            pick = pick_sensor.current()

            time_vals.append(now)
            fret_vals.append(fret)
            damper_vals.append(damper)
            pick_vals.append(pick)

            # Remove old values beyond the window
            while time_vals and (now - time_vals[0]) > window_duration:
                time_vals.popleft()
                fret_vals.popleft()
                damper_vals.popleft()
                pick_vals.popleft()

            line_fret.set_data(time_vals, fret_vals)
            line_damper.set_data(time_vals, damper_vals)
            line_pick.set_data(time_vals, pick_vals)

            ax.set_xlim(max(0, now - window_duration), now)

        except Exception as e:
            print(f"[Plot ERROR] {e}")

        return line_fret, line_damper, line_pick

    ani = FuncAnimation(fig, update, interval=interval, blit=False)
    plt.show()


# Convert the file to a stream
parsed_work = converter.parse('ChromaticScale.xml')

# Depth-first search traversal
recurse_work = parsed_work.recurse()

# Create a list to store the notes in chronological order
notes_in_chronological_order = []

# Iterate through all note objects in the score and add them to the list
for element in recurse_work.notes:
    notes_in_chronological_order.append(element)

# Sort the notes by their start times
notes_in_chronological_order.sort(key=lambda note: note.offset)
#parsed_work.plot()
# Iterate through the sorted notes and play them at their respective start times



# Create timestamped filename
# Ensure LogFiles directory exists
log_dir = "LogFiles"
os.makedirs(log_dir, exist_ok=True)

# Create timestamped filename in the directory
timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
filename = os.path.join(log_dir, f"ina260_multirate_{timestamp}.csv")

fret_current_stream = deque(maxlen=20)  # keeps the last 100 samples
threads, file_handle = start_logging_multirate(filename)

def multi_pick(servo, current_stream, times=3, threshold=2000, delay_after_pick=0.3):
    for i in range(times):
        print(f"[MultiPick] Waiting for spike {i+1}/{times}")
        servo.pickWithDamp(current_stream, threshold)
        print(f"[MultiPick] Pick {i+1} complete")
        time.sleep(delay_after_pick)  # allow servo to complete motion before next pick


def motion_sequence():
    while True:
        print("[Motion] Starting step...")
        fret3.on()

        with concurrent.futures.ThreadPoolExecutor() as executor:
            future = executor.submit(multi_pick, servoG, fret_current_stream, 3, 2000)
            future.result()  # Wait until all picks are done

        print("[Motion] All picks complete. Turning off fret.")
        fret3.off()

# Run motion sequence in its own thread so live plot etc. continues
motion_thread = threading.Thread(target=motion_sequence, daemon=True)
motion_thread.start()

try: 
        # Keep main thread alive
        while True:
            time.sleep(0.5)

except KeyboardInterrupt:
        print("Interrupted by user.")
finally:
        stop_logging(threads, file_handle)
        cleanup()
        print(f"Data saved to {filename}")
        print("Exited cleanly.") 