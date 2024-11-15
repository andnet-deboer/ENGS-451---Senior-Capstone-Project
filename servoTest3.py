from gpiozero import Servo
from time import sleep
from gpiozero import PWMOutputDevice
fan = PWMOutputDevice(1)
servo = Servo(13)


try:
	while True:
    		fan.on() 
    		sleep(7)
    		fan.off() 
except KeyboardInterrupt:
	print("Program stopped")
