import time
from gpiozero import Servo
from gpiozero.pins.pigpio import PiGPIOFactory
from config import SERVO_PINS
from estop import EStopMonitor

class ServoController:
    def __init__(
        self,
        pin,
        factory=None,
        state=True,
        damp=False,
        sustainFactor=2,
        initial_value=0,
        name=None,
        LOW=-30,
        HIGH=30,
        offset=0,
        estop=None
    ):
        if factory is None:
            factory = PiGPIOFactory()
        self.name = name
        self.pin = pin
        self.state = state
        self.servo = Servo(pin, pin_factory=factory, initial_value=offset / 90)
        self.offset = offset
        self.low = LOW + offset
        self.high = HIGH + offset
        self.damped = damp
        self.sustainFactor = sustainFactor
        # Use the shared E‑stop monitor, or create one if none provided
        self.estop = estop or EStopMonitor()

    def set_angle(self, angle):
        self.estop.require_safe()
        self.servo.value = angle / 90

    def count(self, count, bpm):
        # counts out “pick” calls at the given bpm
        for _ in range(count):
            duration = 60.0 / bpm
            self.pick()
            time.sleep(duration)

    def pickWithDuration(self, duration, damp=True):
        self.estop.require_safe()
        self.sustain()
        time.sleep(duration)
        if damp:
            self.damp()

    def pick(self, damp=True):
        self.estop.require_safe()
        self.sustain()
        if damp:
            self.damp()

    def pickWithDamp(self):
        self.estop.require_safe()
        # direct toggle between low/high endpoints
        if self.state:
            self.set_angle(self.low)
            self.state = False
        else:
            self.set_angle(self.high)
            self.state = True
        self.damped = True

    def sustain(self):
        self.estop.require_safe()
        # move to intermediate “sustain” position
        self.damped = False
        low_mid = self.high - ((abs(self.high) + abs(self.low)) / self.sustainFactor)
        high_mid = self.low + ((abs(self.high) + abs(self.low)) / self.sustainFactor)

        if self.state:
            self.set_angle(low_mid)
            self.state = False
        else:
            self.set_angle(high_mid)
            self.state = True

    def hold(self):
        self.estop.require_safe()
        # hold at half‑angle if not damped, full if damped
        if self.state:
            target = self.high if self.damped else (self.high / self.sustainFactor)
        else:
            target = self.low if self.damped else (self.low / self.sustainFactor)
        self.set_angle(target)

    def damp(self):
        self.estop.require_safe()
        if not self.damped:
            # move fully to one end based on current state
            target = self.high if self.state else self.low
            self.set_angle(target)
            self.damped = True

    def zero(self):
        self.estop.require_safe()
        # return to offset “zero” position
        self.set_angle(self.offset)

    def detach(self):
        # doesn’t move the servo, so no E‑stop check
        if getattr(self.servo, 'pwm_device', None):
            try:
                self.servo.detach()
            except Exception as e:
                print(f"[ServoController] Failed to detach servo on pin {self.pin}: {e}")
        else:
            print(f"[ServoController] Servo on pin {self.pin} not fully initialized.")

    def close(self):
        # cleanup PWM resources
        try:
            self.servo.close()
        except Exception as e:
            print(f"[ServoController] Failed to close servo on pin {self.pin}: {e}")
