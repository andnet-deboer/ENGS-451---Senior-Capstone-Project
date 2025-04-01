from relay import Relay
from servo import ServoController
from gpiozero.pins.pigpio import PiGPIOFactory

class Bass:
    def __init__(self, factory=PiGPIOFactory()):
        # Create relays
        self.fret1 = Relay(3)
        self.fret2 = Relay(1)
        self.fret3 = Relay(4)
        self.fret4 = Relay(2)
        self.damper = Relay(5)

        # Create servos
        self.servoE = ServoController(24, name='E', factory=factory)
        self.servoA = ServoController(18, name='A', factory=factory)
        self.servoD = ServoController(27, name='D', factory=factory)
        self.servoG = ServoController(10, name='G', factory=factory)

        self.servos = [self.servoE, self.servoA, self.servoD, self.servoG]
        self.frets = [self.fret1, self.fret2, self.fret3, self.fret4]

    def relay_off(self, except_fret=None):
        for fret in self.frets:
            if fret != except_fret:
                fret.off()

    def detach_servos(self, except_servo=None):
        for servo in self.servos:
            if servo != except_servo:
                servo.detach()

    def zero_servos(self):
        for servo in self.servos:
            servo.zero()
