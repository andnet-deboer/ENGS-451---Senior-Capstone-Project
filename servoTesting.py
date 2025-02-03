#READ THIS! to run this code first run the command below:
#sudo pigpiod
from gpiozero import Servo
from gpiozero.pins.pigpio import PiGPIOFactory
from time import sleep
import time
import numpy as np
import lib8relind
import RPi.GPIO as GPIO
import atexit
# Import necessary libraries
from music21 import *
import time
import concurrent.futures

#  Servo Motor connnectios #
"  E    A     D    G"
"  |    |     |    |"
"  |    |     |    |"
"  |    |     |    |"
"  |    |     |    |"
"  24   18    27   10"

factory = PiGPIOFactory()
initial_value = 0

servoG = Servo(10, pin_factory=factory, initial_value=initial_value)
servoD = Servo(27, pin_factory=factory, initial_value=initial_value)
servoA = Servo(18, pin_factory=factory, initial_value=initial_value)
servoE = Servo(24, pin_factory=factory, initial_value=initial_value)
# Variables
bpm        =  60    # beats per minute
low_angle  = -45    # min -90 degrees
high_angle = -5    # max  90 degrees
increment  = 0.05
start_time = time.time()

def count(count, bpm, servo, low_angle=-45, high_angle=-5): 
    cnt = 0
    while count >= cnt:
        servo.value = low_angle / 90
        sleep(60 / (1.01*bpm))
        cnt +=1            
        servo.value = high_angle / 90
        sleep(60 / (1.01*bpm))
        cnt += 1

def detach_servos(except_servo=None):
    if except_servo != servoG:
        servoG.detach()
    if except_servo != servoD:
        servoD.detach()
    if except_servo != servoA:
        servoA.detach()
    if except_servo != servoE:
        servoE.detach()

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
    GPIO.cleanup()

def run_servo(servo):
    count(-1, bpm, servo)
# Define the dictionary mapping notes to servos
note_to_servo = {
    'A': servoA,
    'G': servoG,
    'E': servoE,
    'D': servoD,
    # Add more mappings as needed
}

''' Play notes with increasing tempo'''
def acceleratedBPM(startBpm=60, maxBpm=140, step=20, strokes=5, servo=servoA):
    for i in range(startBpm, maxBpm, step):
        print(f"Current BPM: {i}")
        print(f"Current Stroke: {strokes}")
        print(f"Current Servo: {servo}")
        count(strokes, i, servo, low_angle=LOW, high_angle=HIGH)
try:
    while True:
      LOW = -14
      HIGH = 1
      BPM = 60
      #acceleratedBPM(100, 120, 20, 1, servoG)
      #acceleratedBPM(80, 200, 10, 5, servoA)
      count(1000, BPM, servoA, low_angle=LOW, high_angle=HIGH)
      


except KeyboardInterrupt:
    print("Program stopped")
    cleanup()

except Exception as e:
    print(f"An error occurred: {e}")
    cleanup()