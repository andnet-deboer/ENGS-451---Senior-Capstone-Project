from gpiozero import Servo
from gpiozero.pins.pigpio import PiGPIOFactory
from time import sleep

class ServoController:
    def __init__(self, pin, factory=None, state=True, initial_value=0, name=None, LOW=-30, HIGH=30, offset=0):
        if factory is None:
            factory = PiGPIOFactory()
        self.name = name
        self.pin = pin
        self.state = state
        self.servo = Servo(pin, pin_factory=factory, initial_value=initial_value)
        self.offset = offset/90
        self.low = LOW+offset
        self.high = HIGH+offset

    def set_angle(self, angle):
        self.servo.value = angle / 90

    def count(self, count, bpm, low_angle=-45, high_angle=-5):
        cnt = 0
        while count >= cnt:
            self.set_angle(low_angle)
            sleep(60 / (1.0 * bpm))
            cnt += 1
            self.set_angle(high_angle)
            sleep(60 / (1.0 * bpm))
            cnt += 1
    ''''
    PICK A STRING
    @param state (low=0) (high=1)
    @param low   (low angle)
    @param high  (high angle)
    '''
    def pick(self):
        if self.state:
            self.set_angle(self.low)
            self.state = False
        else:
            self.set_angle(self.high)
            self.state = True

    def pickWithDamp(self, current_stream, threshold=2000, timeout=2.0, poll_interval=0.01):
        import time
        start = time.time()
        while (time.time() - start) < timeout:
            if len(current_stream) >= 2:
                recent_values = list(current_stream)[-2:]
                if any(c > threshold for c in recent_values):
                    print(f"[{self.name}] Spike detected, picking")
                    self.pick()
                    return
            time.sleep(poll_interval)
        print(f"[{self.name} WARNING] No spike detected in {timeout}s.")

    def detach(self):
        self.servo.detach()

    def zero(self):
        self.servo.value = 0+self.offset
    
    def hold(self):
        if self.state:
            self.servo.value =self.high/90
        self.servo.value = self.low/90

    def on(self):
        self.servo.value = 1

    def close(self):
            self.servo.close()

  
