#READ THIS! to run this code first run the command below:
#sudo pigpiod
from gpiozero import Servo
import lib8relind
from gpiozero.pins.pigpio import PiGPIOFactory
from time import sleep
import time
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
fret1 = Relay(1)
fret2 = Relay(2)
fret3 = Relay(3)
fret4 = Relay(4)

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
    def __init__(self, pin, factory=factory, initial_value=0, name=None):
        self.name = name
        self.servo = Servo(pin, pin_factory=factory, initial_value=initial_value)
        self.pin = pin
        self.state = False
        
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
    def pick(self,low, high):
        if (self.state):
            self.set_angle(low)
            self.state = False
        else:
            self.set_angle(high)
            self.state = True
            
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

def log_current_sensor(filename="ina260_data_fretCurrentSensor.csv"):
    fretCurrentSensor = CurrentSensor(0x44)
    damperCurrentSensor = CurrentSensor(0x41)
    servoCurrentSensor = CurrentSensor(0x40)
    start = time.time()
    with open(filename, "w") as f:
        f.write("Time(s),Current(mA),Voltage(V)\n")
        while logging_active:
            try:
                t = time.time() - start
                current = fretCurrentSensor.current()
                voltage = fretCurrentSensor.voltage()
                f.write(f"{t:.3f},{current:.2f},{voltage:.2f}\n")
                f.flush()
                print(f"[LOG] Time: {t:.2f}s, Current: {current:.2f}mA, Voltage: {voltage:.2f}V")
                time.sleep(0.2)
            except Exception as e:
                print(f"[LOG ERROR] {e}")

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
timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
filename = f"ina260_data_new_{timestamp}.csv"

# Start the logger thread
logging_active = True
log_thread = threading.Thread(target=log_current_sensor, args=(filename,))
log_thread.start()

try:
    while True:
        # Play the solenoid sequence
        chromaticScale()

        # Optionally loop the scale or wait here
        # time.sleep(5)  # Give logger time after playing

except KeyboardInterrupt:
    print("Interrupted by user.")
    logging_active = False
    log_thread.join()  # Ensure the logger thread finishes before exiting

finally:
    cleanup()
    print(f"Data saved to {filename}")
    print("Exited cleanly.")

