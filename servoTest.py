#READ THIS! to run this code first run the command below:
#sudo pigpiod
from gpiozero import Servo
from gpiozero.pins.pigpio import PiGPIOFactory
from time import sleep
import time
import numpy as np
import lib8relind
from time import sleep
factory = PiGPIOFactory()
servo = Servo(13, pin_factory=factory)

# Variables
bpm        = 75    # beats per minute
low_angle  = 65    # min -90 degrees
high_angle = 40   # max  90 degrees
increment  = 0.05
start_time = time.time()
def count(count,bpm): 
	cnt = 0
	while count>=cnt:
		servo.value = low_angle/90
		#lib8relind.set(0,6,1)
		sleep(60/(2*bpm))			
		servo.value = high_angle/90
		sleep(60/(2*bpm))
		#lib8relind.set(0,6,0)
		cnt = cnt +1
def relaySync(count,bpm): 
	cnt = 0
	left = True
	right = False
	#nextNoteSameString = True
	while count>=cnt:
		sleep(60/(2*bpm))
		lib8relind.set(0,6,1)
		if (left):
			servo.value = low_angle/90
			sleep(60/(2*bpm))		
		if (right):
			servo.value = high_angle/90
			sleep(60/(3*bpm))
		#if(!nextNoteSameString):
		lib8relind.set(0,6,0)
			
		left, right = right, left
		cnt = cnt +1
def moveRange():
	for i in range(-10,10,1):
		servo.value = i/10
		sleep(0.1)
		print(i/10)
		
			
try:
	while True:
		#servo.value = 0
		#count(10,75)
		#sleep(1)
		relaySync(1,30)
		#sleep(1)
		#count(2,10)
		#sleep(1.5)
		#servo.value = 0.5
		#sleep(60/(2*bpm))			
		#servo.value = -0.5
		#sleep(60/(2*bpm))
		#moveRange()


except KeyboardInterrupt:
	print("Program stopped")
	servo.detach() # stop servo motion
	
