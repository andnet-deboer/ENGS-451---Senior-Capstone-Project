from config import (
    SERVO_PINS,
    RELAY_NUMBERS,
    DAMP_THRESHOLD,
    FRET_THRESHOLD,
    RELEASE_THRESHOLD,
    DELAY_AFTER_PICK,
    NOTE_MAPPING_KEYS

)
from servo import ServoController
from relay import Relay
from gpiozero.pins.pigpio import PiGPIOFactory
import time

class Bass:
    def __init__(self, factory=PiGPIOFactory()):
        # Create relays
        self.fret1 = Relay(RELAY_NUMBERS['fret1'])
        self.fret2 = Relay(RELAY_NUMBERS['fret2'])
        self.fret3 = Relay(RELAY_NUMBERS['fret3'])
        self.fret4 = Relay(RELAY_NUMBERS['fret4'])
        self.damper = Relay(RELAY_NUMBERS['damper'])

        # Create servos
        self.servoE = ServoController(SERVO_PINS['E'], name='E', factory=factory)
        self.servoA = ServoController(SERVO_PINS['A'], name='A', factory=factory,LOW=10,HIGH=35)
        self.servoD = ServoController(SERVO_PINS['D'], name='D', factory=factory)
        self.servoG = ServoController(SERVO_PINS['G'], name='G', factory=factory)

        self.servos = [self.servoE, self.servoA, self.servoD, self.servoG]
        self.frets = [self.fret1, self.fret2, self.fret3, self.fret4]
  
        # Create the note mapping using object references from symbolic config
        self.note_mapping = {
            key: [getattr(self, f"servo{servo_letter}"), getattr(self, fret_name) if fret_name else None]
            for key, (servo_letter, fret_name) in NOTE_MAPPING_KEYS.items()
        }


    def detach_servos(self, except_servo=None):
        for servo in self.servos:
            if servo != except_servo:
                servo.detach()

    def relay_off(self, keep=[]):
        for fret in self.frets:
            if fret not in keep:
                fret.off()

    def bass_off(self):
        self.detach_servos()
        self.relay_off()


    def zero_servos(self):
        for servo in self.servos:
            servo.zero()

    def pick_string(self, note_name, octave, damper_stream, fret_stream, timeout=2.0):
        mapping = self.note_mapping.get((note_name, octave),duration=0)
        if not mapping:
            print(f"[Bass] Note ({note_name}, {octave}) not found in mapping.")
            return

        servo, fret = mapping

        # 1. Damp String
        self.damper.on()
        print(f"[Bass] Damper ON")

        # 2. Wait for damper pressure
        if not self._wait_for_threshold(damper_stream, DAMP_THRESHOLD, timeout):
            print(f"[Bass] Warning: Damper current never exceeded {DAMP_THRESHOLD}")
            return

        # If no fret needed (open string), skip fretting steps
        if fret is not None:
            self.relay_off(keep=[fret])
            fret.on()
            print(f"[Bass] Fret ON: {fret}")

            if not self._wait_for_threshold(fret_stream, FRET_THRESHOLD, timeout):
                print(f"[Bass] Warning: Fret current never exceeded {FRET_THRESHOLD}")
                return
        else:
            self.relay_off()

        # 5. Release damper
        self.damper.off()
        print(f"[Bass] Damper OFF")

        if not self._wait_until_below_threshold(damper_stream, RELEASE_THRESHOLD, timeout):
            print(f"[Bass] Warning: Damper current never dropped below {RELEASE_THRESHOLD}")
            return

        # 7. Pick
        print(f"[Bass] Picking note {note_name}{octave}")
        servo.pick()
        time.sleep(0.8*duration)
        self.relay_off()


    def _wait_for_threshold(self, current_stream, threshold, timeout=2.0, poll_interval=0.01):
        start = time.time()
        while (time.time() - start) < timeout:
            if len(current_stream) >= 2:
                if any(c > threshold for c in list(current_stream)[-2:]):
                    return True
            time.sleep(poll_interval)
        return False

    def _wait_until_below_threshold(self, current_stream, threshold, timeout=2.0, poll_interval=0.01):
        start = time.time()
        while (time.time() - start) < timeout:
            if len(current_stream) >= 2:
                if all(c < threshold for c in list(current_stream)[-2:]):
                    return True
            time.sleep(poll_interval)
        return False
