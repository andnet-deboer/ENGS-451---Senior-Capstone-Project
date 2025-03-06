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


try:
    while True:
      zero_servos

except KeyboardInterrupt:
    print("Program stopped")
    cleanup()

except Exception as e:
    print(f"An error occurred: {e}")
    cleanup()