import lib8relind
from time import sleep


lib8relind.set_all(0,0)

def Relay() :
	def _init_():
		self.stack = 0;

	def set(relay, value):
		if (relay == 6):
			relay = 7
		if (relay == 7):
			relay = 6
		lib8relind.set(self.stack, relay, value)
		
	def get (relay):
		lib8relind.get(self.stack, relay)

while True:
	for i in range(1,8,1):
		if (i == 6):
			i = 7
		lib8relind.set(0, i, 1)
		print("############### NEW COMMAND ############################\n")
		print ("Relay: " + str(i))
		print ("Value: " + str(lib8relind.get(0,i)))
		sleep(1)
		if (i == 7):
			lib8relind.set(0, 6, 1)
			print("######### NEW COMMAND############################\n")
			print ("Relay: " + str(i))
			print ("Value: " + str(lib8relind.get(0,i)))
			sleep(1)
	lib8relind.set_all(0,0)

