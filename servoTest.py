#READ THIS! to run this code first run the command below:
#sudo pigpiod
from gpiozero import Servo
from gpiozero.pins.pigpio import PiGPIOFactory
from time import sleep
import time
import numpy as np
import lib8relind
import RPi.GPIO as GPIO
from time import sleep
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

def count(count,bpm,servo): 
	cnt = 0
	while count>=cnt:
		servo.value = low_angle/90
		sleep(60/(2*bpm))			
		servo.value= high_angle/90
		sleep(60/(2*bpm))
		cnt = cnt +1

# def relaySync(count,bpm,): 
# 	cnt = 0
# 	left = True
# 	right = False
# 	#nextNoteSameString = True
# 	while count>=cnt:
# 		sleep(60/(2*bpm))
# 		lib8relind.set(0,6,1)
# 		if (left):
# 			servo.value = low_angle/90
# 			sleep(60/(2*bpm))		
# 		if (right):
# 			servo.value = high_angle/90
# 			sleep(60/(3*bpm))
# 		#if(!nextNoteSameString):
# 		lib8relind.set(0,6,0)
			
# 		left, right = right, left
# 		cnt = cnt +1

def moveRange():
	for i in range(-8,8,1):
		servoD.value = 0
		servoA.value = 0
		servoG.value = 0
		servoE.value = i/10
		sleep(0.05)
		print(i/10)

def cleanup():
    servoG.detach()
    servoD.detach()
    servoA.detach()
    servoE.detach()
    GPIO.cleanup()
		
try:
	while True:
		servoG.detach()
		servoD.detach()
		servoA.detach()
		count(10,bpm,servoA)
		#sleep(2)
		#moveRange()


except KeyboardInterrupt:
	print("Program stopped")
	cleanup()

except Exception as e:
    print(f"An error occurred: {e}")
    cleanup()

