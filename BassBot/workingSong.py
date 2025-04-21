#READ THIS! to run this code first run the command below:
#sudo pigpiod
import csv
from queue import Full
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


# Import necessary libraries
#from music21 import *
import time
from datetime import timedelta
import concurrent.futures

#  Servo Motor connnectios #
"               E    A     D    G"
" Fret 1        |    |     |    |   "
" Fret 2        |    |     |    |   "
" Fret 3        |    |     |    |   "
" Fret 4        |    |     |    |   "
"              24   27    18   10   "

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
    def __init__(self):
        self.i2c = board.I2C()  # uses board.SCL and board.SDA
        # i2c = board.STEMMA_I2C()  # For using the built-in STEMMA QT connector on a microcontroller
        self.ina260 = adafruit_ina260.INA260(self.i2c)
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
fret1 = Relay(3)
fret2 = Relay(1)
fret3 = Relay(4)
fret4 = Relay(2)
fret0 = Relay(10) #open string
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
    def __init__(self, pin, factory=factory, initial_value=0, LOW=-30, HIGH = 30,offset=0, name=None):
        self.name = name
        self.servo = Servo(pin, pin_factory=factory, initial_value=initial_value)
        self.pin = pin
        self.state = True
        self.low = LOW
        self.high= HIGH
        self.offset=offset
        
    def set_angle(self, angle):
        # Convert angle (-90 to 90) to value (-1 to 1)
        self.servo.value = (angle+self.offset) / 90
        
    def count(self, count, bpm, low_angle=-45, high_angle=-5):
        """ Move the servo back and forth for a set count at a given BPM """
        cnt = 0
        while cnt < count:
            self.set_angle(low_angle)
            sleep(60 / bpm)
            cnt += 1
            self.set_angle(high_angle)
            sleep(60 / bpm)
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
            
    def detach(self):
        self.servo.detach()
        
    def zero(self):
        self.servo.value = 0+self.offset
        
    def on(self):
        self.servo.value = 1

#Initialize servos 
servoG = ServoController(18, factory=factory, LOW=-25, HIGH=25,offset=10, name='G')
servoD = ServoController(24, factory=factory, LOW=-20, HIGH=20,offset=4, name='D')
servoA = ServoController(27, factory=factory, LOW=-15, HIGH=15, name='A')
servoE = ServoController(10, factory=factory, LOW=-25, HIGH=25, name='E')

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
#None indicates the open string
note_mapping = {
    ('E', 2): [servoE, None],
    ('F', 2): [servoE, fret1],
    ('F#', 2): [servoE, fret2],
    ('G', 2): [servoE, fret3],
    ('G#', 2): [servoE, fret4],
    ('A', 2): [servoA, None],
    ('A#', 2): [servoA, fret1],
    ('B', 2): [servoA, fret2],
    ('C', 3): [servoA, fret3],
    ('C#', 3): [servoA, fret4],
    ('D', 3): [servoD, None],
    ('D#', 3): [servoD, fret1],
    ('E', 3): [servoD, fret2],
    ('F', 3): [servoD, fret3],
    ('F#', 3): [servoD, fret4],
    ('G', 3): [servoG, None],
    ('G#', 3): [servoG, fret1],
    ('A', 3): [servoG, fret2],
    ('A#', 3): [servoG, fret3],
    ('B', 3): [servoG, fret4]
}

def timePerBeat(bpm=120,timeSignature=4):
    #check if BMP is spceified by musicXML file

    #if not use default bpm of 120

    #get the current time signature

    #return (2*60*timeSignature)/(4*bpm)
    return (60*timeSignature)/(4*bpm)
    

''' Play notes with increasing tempo'''
def acceleratedBPM(startBpm=60, maxBpm=140, step=40, strokes=5, servo=servoA, servo2=servoG):
    for i in range(startBpm, maxBpm, step):
        print(f"Current BPM: {i}")
        print(f"Current Stroke: {strokes}")
        print(f"Current Servo: {servo}")
        count(strokes, i, servo, low_angle=LOW, high_angle=HIGH)
        count(strokes, i, servo2, low_angle=LOW, high_angle=HIGH)

# def chromaticScale(delay=0.6):
#         time.sleep(delay/2)
#         fret1.on()
#         print("Fret1")
#         time.sleep(delay/5)
#         servoE.pick()
#         print("ServoE")
#         time.sleep(delay)
#         fret1.off()
        
#         time.sleep(delay/2)
#         fret2.on()
#         print("Fret2")
#         time.sleep(delay/2)
#         servoA.pick()
#         print("ServoA")
#         time.sleep(delay)
#         fret2.off()

#         time.sleep(delay/2)
#         fret3.on()
#         print("Fret3")
#         time.sleep(delay/2)
#         servoD.pick()
#         print("ServoD")
#         time.sleep(delay)
#         fret3.off()

#         time.sleep(delay/2)
#         fret4.on()
#         print("Fret4")
#         time.sleep(delay/2)
#         servoG.pick()
#         print("ServoG")
#         time.sleep(delay)
#         fret4.off()

# Convert the file to a stream
#parsed_work = converter.parse('ChromaticScale.xml')

def save_to_csv_with_timing(musicFile="7NationArmy.xml", filename="output_with_timing.csv"):
    parsed_work = converter.parse(musicFile)
    # Depth-first search traversal
    recurse_work = parsed_work.recurse().notesAndRests
    # Initialize time
    trackTime = 0
    note_matrix = []

    with open(filename, mode='w', newline='') as file:
        writer = csv.writer(file)
        writer.writerow(["Element", "Note/Rest", "Start Time", "End Time", "Duration"])  # Write the header row
        for element in recurse_work:
            if element.isNote:
                start_time = timedelta(seconds=trackTime)
                duration = element.duration.quarterLength * timePerBeat()
                trackTime += duration
                end_time = timedelta(seconds=trackTime)
                row = [element, element.name + str(element.octave), str(start_time), str(end_time), duration]
                writer.writerow(row)
                note_matrix.append(row)
            else:
                start_time = timedelta(seconds=trackTime)
                duration = element.duration.quarterLength * timePerBeat()
                trackTime += duration
                end_time = timedelta(seconds=trackTime)
                row = [element, element.name, str(start_time), str(end_time), duration]
                writer.writerow(row)
                note_matrix.append(row)

    return note_matrix

# Call the function and get the note matrix
#note_matrix = save_to_csv_with_timing("ChromaticScale.xml", "output_with_timing.csv")
note_matrix = save_to_csv_with_timing()


notes_in_chronological_order = []

# # Iterate through all note objects in the score and add them to the list
# for element in recurse_work.notes:
#     notes_in_chronological_order.append(element)

# # Sort the notes by their start times
# notes_in_chronological_order.sort(key=lambda note: note.offset)
# #parsed_work.plot()
# Iterate through the sorted notes and play them at their respective start times


# def play_notes(note_matrix):
#   for i in range(len(note_matrix) - 1):  # Iterate up to the second-to-last row
#             current_row = note_matrix[i]
#             next_row = note_matrix[i + 1]  # Access the next row

#             note = current_row[0]
#             if note.isNote:
#                  octave = current_row[0].octave+1
#             else:
#                 octave = 0
           
#             current_time = current_row[2]
#             next_time = next_row[2]  # Access a value from the next row
#             duration = current_row[4]

#             if note.isNote:
#                 #All non open string notes
#                 if note_mapping[note.name,octave][1] is not None:
#                     relay_off(note_mapping[note.name,octave][1])  # Unfret all other frets
#                     note_mapping[note.name,octave][1].on()  # Fret the note
#                     note_mapping[note.name,octave][0].pick()  # Pick the note
#                 #Open string notes
#                 elif note_mapping[note.name,octave][1] is None:
#                     lib8relind.set_all(0, 0)
#                     note_mapping[note.name,octave][0].pick()  # Pick the note
#                 time.sleep(duration)
#             else:
#                 time.sleep(duration)
#                 lib8relind.set_all(0, 0)

# bpm = setBPM()
try:
    while True:
  

        LOW = -30
        HIGH = 30 
        BPM = 120

        #Initalize 
        
        #chromaticScale(1)
        # play_notes(note_matrix)
        #servoG.pick()
        #time.sleep(1)
     
        # note_mapping['E'][1].on()  # Fret the note
        # note_mapping['E'][0].pick()  # Pick the note
        # time.sleep(1)
        # note_mapping['E'][1].off()
        # time.sleep(1)

     
      


    

except KeyboardInterrupt:
    print("Program stopped")
    cleanup()

except Exception as e:
    print(f"An error occurred: {e}")
    cleanup()
