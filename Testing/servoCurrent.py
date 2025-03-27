import time
import threading
import matplotlib.pyplot as plt
import matplotlib.animation as animation

from gpiozero import Servo
from gpiozero.pins.pigpio import PiGPIOFactory
import lib8relind
import RPi.GPIO as GPIO
import board
import adafruit_ina260
import atexit

# ====== Setup =======
factory = PiGPIOFactory()
start_time = time.time()
plot_running = True

# ====== Relay Class ======
class Relay:
    def __init__(self, relay_number):
        self.relay_number = relay_number

    def on(self):
        relay = self.relay_number
        if relay == 6:
            relay = 7
        elif relay == 7:
            relay = 6
        lib8relind.set(0, relay, 1)

    def off(self):
        relay = self.relay_number
        if relay == 6:
            relay = 7
        elif relay == 7:
            relay = 6
        lib8relind.set(0, relay, 0)

# ====== Servo Class ======
class ServoController:
    def __init__(self, pin, factory=factory, LOW=-15, HIGH=15, offset=0, name=None):
        self.name = name
        self.servo = Servo(pin, pin_factory=factory, initial_value=0)
        self.low = LOW
        self.high = HIGH
        self.offset = offset
        self.state = True

    def set_angle(self, angle):
        self.servo.value = (angle + self.offset) / 90

    def pick(self):
        if self.state:
            self.set_angle(self.low)
        else:
            self.set_angle(self.high)
        self.state = not self.state

    def detach(self):
        self.servo.detach()

# ====== Relay Initialization ======
fret1 = Relay(1)
fret2 = Relay(2)
fret3 = Relay(3)
fret4 = Relay(4)

def relay_off(except_fret=None):
    for fret in [fret1, fret2, fret3, fret4]:
        if fret != except_fret:
            fret.off()

# ====== Servo Initialization ======
servoE = ServoController(18, LOW=-15, HIGH=15, name="E")
servoA = ServoController(27, LOW=-15, HIGH=15, name="A")
servoD = ServoController(24, LOW=-20, HIGH=20, offset=4, name="D")
servoG = ServoController(10, LOW=-15, HIGH=15, name="G")

def detach_servos():
    for servo in [servoE, servoA, servoD, servoG]:
        servo.detach()

def detach_relays():
    lib8relind.set_all(0, 0)

def cleanup():
    detach_servos()
    detach_relays()
    GPIO.cleanup()

atexit.register(cleanup)

# ====== INA260 Sensor Class ======
class CurrentSensor:
    def __init__(self):
        self.i2c = board.I2C()
        self.ina260 = adafruit_ina260.INA260(self.i2c)

    def current(self):
        return self.ina260.current

    def voltage(self):
        return self.ina260.voltage

    def power(self):
        return self.ina260.power

# ====== Real-Time Plotting ======
current_data = {
    "times": [],
    "currents": []
}

def update_plot(i):
    plt.cla()
    plt.title("Live Current Draw (INA260)")
    plt.xlabel("Time (s)")
    plt.ylabel("Current (mA)")
    if current_data["times"]:
        plt.plot(current_data["times"], current_data["currents"], label="Current (mA)")
        plt.legend(loc="upper right")

def start_plotting():
    fig = plt.figure()
    ani = animation.FuncAnimation(fig, update_plot, interval=500)
    plt.tight_layout()
    plt.show()

def log_current_sensor():
    sensor = CurrentSensor()
    global plot_running

    try:
        with open("ina260_data.csv", "w") as f:
            f.write("Time(s),Current(mA),Voltage(V)\n")
            while plot_running:
                try:
                    current = sensor.current()
                    voltage = sensor.voltage()
                    t = time.time() - start_time

                    current_data["times"].append(t)
                    current_data["currents"].append(current)

                    # Write to CSV
                    f.write(f"{t:.3f},{current:.2f},{voltage:.2f}\n")
                    f.flush()

                    # Keep only recent data for plotting
                    if len(current_data["times"]) > 100:
                        current_data["times"] = current_data["times"][-100:]
                        current_data["currents"] = current_data["currents"][-100:]

                    time.sleep(0.2)
                except Exception as e:
                    print("Sensor read error:", e)
    except Exception as e:
        print(f"File write error: {e}")


# ====== Thread Setup ======
sensor_thread = threading.Thread(target=log_current_sensor)
plot_thread = threading.Thread(target=start_plotting)
sensor_thread.start()
plot_thread.start()

# ====== Main Play Loop ======
try:
    delay = 2
    while True:
        time.sleep(delay/2)
        fret1.on()
        time.sleep(delay/5)
        servoE.pick()
        print("ServoE")
        time.sleep(delay)
        fret1.off()

        time.sleep(delay/2)
        fret2.on()
        time.sleep(delay/2)
        servoA.pick()
        print("ServoA")
        time.sleep(delay)
        fret2.off()

        time.sleep(delay/2)
        fret3.on()
        time.sleep(delay/2)
        servoD.pick()
        print("ServoD")
        time.sleep(delay)
        fret3.off()

        time.sleep(delay/2)
        fret4.on()
        time.sleep(delay/2)
        servoG.pick()
        print("ServoG")
        time.sleep(delay)
        fret4.off()

except KeyboardInterrupt:
    print("Program stopped by user.")
    plot_running = False
    sensor_thread.join()
    cleanup()

except Exception as e:
    print(f"An error occurred: {e}")
    plot_running = False
    sensor_thread.join()
    cleanup()
