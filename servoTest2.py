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



try:
	while True:
		servo.max()
		sleep(1)
		servo.min()
		sleep(1)
	

except KeyboardInterrupt:
	print("Program stopped")
	servo.detach() # stop servo motion
	
