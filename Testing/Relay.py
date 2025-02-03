import lib8relind
from time import sleep

while True:
	lib8relind.set(0,6,1)
	sleep(0.3)
	lib8relind.set(0, 6,0)
	sleep(0.3)



