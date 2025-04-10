import pigpio
from config import ESTOP_PIN

class EStopMonitor:
    def __init__(self, gpio_pin=ESTOP_PIN):
        self.gpio_pin = gpio_pin
        self.pi = pigpio.pi()
        if not self.pi.connected:
            raise RuntimeError("Could not connect to pigpiod. Is it running?")
        self.pi.set_mode(self.gpio_pin, pigpio.INPUT)
        self.pi.set_pull_up_down(self.gpio_pin, pigpio.PUD_UP)

    def is_triggered(self):
        return self.pi.read(self.gpio_pin) == 1  # HIGH means e-stop is pressed

    def require_safe(self):
        if self.is_triggered():
            raise RuntimeError("🚨 E-Stop is PRESSED. Action blocked for safety.")
