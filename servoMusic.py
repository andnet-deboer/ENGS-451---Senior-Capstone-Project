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
import os
# Import necessary libraries
from music21 import *
import time
import concurrent.futures

# Convert the file to a stream
#parsed_work = converter.parse('Two-bar C major scale.xml')
#arsed_work = converter.parse('7_Nation_Army.musicxml')
parsed_work = converter.parse('Viva_La_Vida_by_Coldplay.musicxml')

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



factory = PiGPIOFactory()
initial_value = 0

servoG = Servo(10, pin_factory=factory, initial_value=initial_value)
servoD = Servo(27, pin_factory=factory, initial_value=initial_value)
servoA = Servo(18, pin_factory=factory, initial_value=initial_value)
servoE = Servo(24, pin_factory=factory, initial_value=initial_value)
# Variables
bpm        =  300    # beats per minute
low_angle  = -45    # min -90 degrees
high_angle = -5    # max  90 degrees
increment  = 0.05
start_time = time.time()

def count(count, bpm, servo, low_angle=-45, high_angle=-5): 
    cnt = 0
    while count >= cnt:
        servo.value = low_angle / 90
        sleep(60 / (2 * bpm))            
        servo.value = high_angle / 90
        sleep(60 / (2 * bpm))
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
    'B': servoA,
    'C': servoG
    # Add more mappings as needed
}

try:
        for element in notes_in_chronological_order:
            time.sleep(element.offset)
            if isinstance(element, note.Note):
                note_name = element.name
                if note_name in note_to_servo:
                    move_servo = note_to_servo[note_name]
                    detach_servos(except_servo=move_servo)
                    count(1, 120,move_servo)
                    # element.show('midi')
                    
                    print(f"Servo {move_servo} moving now")
                else:
                    print(f"Note {note_name} not mapped to any servo")
            elif isinstance(element, chord.Chord):
                print(f"Ignoring chord: {element}")


except KeyboardInterrupt:
    print("Program stopped")
    cleanup()

except Exception as e:
    print(f"An error occurred: {e}")
    cleanup()
finally:
    cleanup()