from gpiozero import CPUTemperature

cpu = CPUTemperature()
print("Temperature Degrees Celcius: " +str(cpu.temperature))
