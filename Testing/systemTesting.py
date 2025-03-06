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
# Import necessary libraries
#from music21 import *
import time
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

servoG = Servo(10, pin_factory=factory, initial_value=initial_value)
servoD = Servo(27, pin_factory=factory, initial_value=initial_value)
servoA = Servo(18, pin_factory=factory, initial_value=initial_value)
servoE = Servo(24, pin_factory=factory, initial_value=initial_value)

#fret1 =  Relay(4)
# Variables
bpm        =  60    # beats per minute
low_angle  = -45    # min -90 degrees
high_angle = -5    # max  90 degrees
increment  = 0.05
start_time = time.time()


class Relay:
    def __init__(self, relay_number):
        self.relay_number = relay_number
        
    def on(self, value=1):
        relay = self.relay_number
        if (relay == 6):
            relay = 7
        elif (relay == 7):
            relay = 6
        lib8relind.set(0, relay, value)

    def off(self, value=0):
        relay = self.relay_number
        if (relay == 6):
            relay = 7
        elif (relay == 7):
            relay = 6
        lib8relind.set(0, relay, value)
        
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

# class ServoController:
#     def __init__(self, pin, factory=factory, initial_value=0, name=None):
#         self.name = name
#         self.servo = Servo(pin, pin_factory=factory, initial_value=initial_value)
#         self.pin = pin
        
#     def set_angle(self, angle):
#         # Convert angle (-90 to 90) to value (-1 to 1)
#         self.servo.value = angle / 90
        
#     def count(self, count, bpm, low_angle=-45, high_angle=-5):
#         cnt = 0
#         while count >= cnt:
#             self.set_angle(low_angle)
#             sleep(60 / (1.0*bpm))
#             cnt += 1
#             self.set_angle(high_angle)
#             sleep(60 / (1.0*bpm))
#             cnt += 1
            
#     def detach(self):
#         self.servo.detach()
        
#     def zero(self):
#         self.servo.value = 0
        
#     def on(self):
#         self.servo.value = 1

# Then initialize your servos like this:
# servoG = ServoController(10, name='G')
# servoD = ServoController(27, name='D')
# servoA = ServoController(18, name='A')
# servoE = ServoController(24, name='E')
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
note_to_servo = {
    'F': servoE,
    'F#': servoE,
    #'G': servoE
    #'Gb': servoG,
   # 'E': servoE,
    #'D': servoD,
    # Add more mappings as needed
}

''' Play notes with increasing tempo'''
def acceleratedBPM(startBpm=60, maxBpm=140, step=40, strokes=5, servo=servoA, servo2=servoG):
    for i in range(startBpm, maxBpm, step):
        print(f"Current BPM: {i}")
        print(f"Current Stroke: {strokes}")
        print(f"Current Servo: {servo}")
        count(strokes, i, servo, low_angle=LOW, high_angle=HIGH)
        count(strokes, i, servo2, low_angle=LOW, high_angle=HIGH)
try:
    while True:
         #for i in range(1,1000000,1):
              #   lib8relind.set(0, 4, 1)
                # sleep(2)
                 #lib8relind.set_all(0,0)
                 #sleep(1)


        LOW = -30
        HIGH = 30
        BPM = 260
        #acceleratedBPM(300, 500, 5, 1, servoG,servoA)
        #acceleratedBPM(60, 200, 5, 1, servoA)
        count(1000, BPM, servoA, low_angle=-65, high_angle=65)

        #count(1, BPM, servoG, low_angle=-30, high_angle=20)
        


except KeyboardInterrupt:
    print("Program stopped")
    cleanup()

except Exception as e:
    print(f"An error occurred: {e}")
    cleanup()
