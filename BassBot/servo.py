import time
from gpiozero import Servo
from gpiozero.pins.pigpio import PiGPIOFactory
from time import sleep
from config import SERVO_PINS


class ServoController:
    def __init__(self, pin, factory=None, state=True,damp=False, sustainFactor=2, initial_value=0, name=None, LOW=-30, HIGH=30, offset=0):
        if factory is None:
            factory = PiGPIOFactory()
        self.name = name
        self.pin = pin
        self.state = state
        self.servo = Servo(pin, pin_factory=factory, initial_value=offset / 90)
        self.offset = offset
        self.low = (LOW+offset)
        self.high = (HIGH+offset)
        self.damped = damp
        self.sustainFactor = sustainFactor

    def set_angle(self, angle):
        self.servo.value = angle / 90

    def count(self, count, bpm):
        cnt = 0
        while count >= cnt:
            duration = 60 / (1.0 * bpm)
            self.pick(duration)
            #sleep())
  
    ''''
    PICK A STRING
    @param state (low=0) (high=1)
    @param low   (low angle)
    @param high  (high angle)
    '''
    def pickWithDuration(self,duration,damp=True):
        self.sustain()
        time.sleep(duration)
        if damp:
            self.damp()

    def pick(self,damp=True):
        self.sustain()
        #time.sleep(duration)
        if damp:
            self.damp()

    def pickWithDamp(self):
        self.damp = True
        if self.state:
            self.set_angle(self.low)
            self.state = False
        else:
            self.set_angle(self.high)
            self.state = True
      
    def sustain(self):
        self.damped = False
        low = self.high-((abs(self.high)+abs(self.low))/self.sustainFactor)
        high = self.low+((abs(self.high)+abs(self.low))/self.sustainFactor)

        if self.state:
            self.set_angle(low)
            self.state = False
        else:
            self.set_angle(high)
            self.state = True
        

    # def pickWithDamp(self, current_stream, threshold=2000, timeout=2.0, poll_interval=0.01):
    #     import time
    #     start = time.time()
    #     while (time.time() - start) < timeout:
    #         if len(current_stream) >= 2:
    #             recent_values = list(current_stream)[-2:]
    #             if any(c > threshold for c in recent_values):
    #                 print(f"[{self.name}] Spike detected, picking")
    #                 self.pick()
    #                 return
    #         time.sleep(poll_interval)
    #     print(f"[{self.name} WARNING] No spike detected in {timeout}s.")

    def detach(self):
        if self.servo is not None and getattr(self.servo, 'pwm_device', None) is not None:
            try:
                self.servo.detach()
            except Exception as e:
                print(f"[ServoController] Failed to detach servo on pin {self.pin}: {e}")
        else:
            print(f"[ServoController] Skipping detach, servo on pin {self.pin} not fully initialized.")

    def zero(self):
        self.set_angle(self.offset)

    def hold(self):
        if self.state:
            if self.damped:
                self.set_angle(self.high)
            else: 
                self.set_angle(self.high/2)
        else:
            if self.damped:
                self.set_angle(self.low)
            else: 
                self.set_angle(self.low/2)
        

    def damp(self):
        if self.damped == False: # if servo is not in a damp pos
            self.damped = True
            if  self.state == True: #if it is east move to max east pos
                self.set_angle(self.high) 
            else:
                self.set_angle(self.low) #if its west move to max west pos        



    def close(self):
            self.servo.close()

# factory=PiGPIOFactory()
# servoA = ServoController(SERVO_PINS['A'], name='A', factory=factory, state=True,sustainFactor=3, LOW=-40,HIGH=20,offset=-8/90)
# servoE = ServoController(SERVO_PINS['E'], name='E', factory=factory, state=True, LOW=-30,HIGH=30,offset=0)
# servoD = ServoController(SERVO_PINS['D'], name='D', factory=factory, state=True, LOW=-30,HIGH=30,offset=0)
# servoG = ServoController(SERVO_PINS['G'], name='G', factory=factory, state=True, LOW=-30,HIGH=30,offset=-8)

# while True: 
#     for i in range(1,10):
#         print("Damping")
#         servoA.pickWithDamp()
#         time.sleep(0.5)
#     for i in range(1,10):
#         print("Sustain")
#         servoA.sustain()
#         time.sleep(0.5)
# # cnt = 0
# # while cnt <= 1:
#     print("Picking")
#     servoA.sustain()
#     time.sleep(2)
#     print("Damping")
#     servoA.damp()
#     time.sleep(2)
#     #cnt = cnt +1
#     #servoA.sustain()
#     #time.sleep(1)
#     #servoA.zero()
#     #servoG.zero()
#     #print("zero servo")
