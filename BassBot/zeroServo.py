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
import bass


#  Servo Motor connnectios #
"  E    A     D    G"
"  |    |     |    |"
"  |    |     |    |"
"  |    |     |    |"
"  |    |     |    |"
"  24   18    27   10"

factory = PiGPIOFactory()
initial_value = 0


bassbot = bass.Bass()

atexit.register(bassbot.bass_off)
def cleanup():
    bassbot.bass_off
    GPIO.cleanup()


try:
    while True:
        bassbot.zero_servos
        

except KeyboardInterrupt:
    print("Program stopped")
    cleanup()

except Exception as e:
    print(f"An error occurred: {e}")
    cleanup()