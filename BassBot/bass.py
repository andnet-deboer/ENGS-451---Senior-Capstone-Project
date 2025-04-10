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
from estop import EStopMonitor

class Bass:
    def __init__(self, factory=PiGPIOFactory()):
        #Create EStop
        self.estop = EStopMonitor()  
        # Create relays
        self.fret1 = Relay(RELAY_NUMBERS['fret1'])
        self.fret2 = Relay(RELAY_NUMBERS['fret2'])
        self.fret3 = Relay(RELAY_NUMBERS['fret3'])
        self.fret4 = Relay(RELAY_NUMBERS['fret4'])
        self.damper = Relay(RELAY_NUMBERS['damper'])

        # Create servos
        self.servoE = ServoController(SERVO_PINS['E'], name='E', factory=factory, state=False, LOW=-35, HIGH=-5, offset=25)
        self.servoA = ServoController(SERVO_PINS['A'], name='A', factory=factory, state=True, LOW=-25,HIGH=5,offset=2)

        self.servoD = ServoController(SERVO_PINS['D'], name='D', factory=factory,state=False, LOW=-10, HIGH=25, offset=0)
        self.servoG = ServoController(SERVO_PINS['G'], name='G', factory=factory,state=True, LOW=-30,HIGH=-5,offset=5)

        self.servos = [self.servoE, self.servoA, self.servoD, self.servoG]
        self.frets = [self.fret1, self.fret2, self.fret3, self.fret4]
  
       
        # Build the note mapping at initialization
        self.note_mapping = {
    key: [getattr(self, f"servo{string}"), getattr(self, fret) if fret else None]
    for key, (string, fret) in NOTE_MAPPING_KEYS.items()
}

    def _build_note_mapping(self):
        from config import NOTE_MAPPING_KEYS
        mapping = {}
        for key, (string_name, fret_name) in NOTE_MAPPING_KEYS.items():
            servo = getattr(self, f"servo{string_name}")
            fret = getattr(self, fret_name) if fret_name else None
            mapping[key] = [servo, fret]
        return mapping


    def detach_servos(self, except_servo=None):
        for servo in self.servos:
            if servo != except_servo:
                servo.detach()
                
    def relay_off(self, except_fret=None):
        for fret in [self.fret1, self.fret2, self.fret3, self.fret4]:
            if fret != except_fret:
                fret.off()

    def bass_off(self):
        self.detach_servos()
        self.relay_off()
   
    def all_relays_off(self):
        for fret in self.frets:
            fret.off()
        self.damper.off()

    def zero_servos(self):
        for servo in self.servos:
            servo.zero()

    def pick_string(self, note_name, octave, fret_stream, timeout=2.0):
        self.estop.require_safe()
        mapping = self.note_mapping.get((note_name, octave),duration=0)
        if not mapping:
            print(f"[Bass] Note ({note_name}, {octave}) not found in mapping.")
            return

        servo, fret = mapping

        servo.pick()
        time.sleep(DELAY_AFTER_PICK)  # Allow servo motion to complete
        print(f"[Bass] Picking note {note_name}{octave}")
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

    def cleanup(self):
        print("[Bass] Cleaning up GPIO devices...")

        for servo in self.servos:
            try:
                servo.close()
            except Exception as e:
                print(f"[Bass] Failed to close servo {servo.name}: {e}")

        for fret in self.frets:
            try:
                fret.off()
            except Exception as e:
                print(f"[Bass] Failed to turn off relay {fret}: {e}")

        try:
            self.damper.off()
        except Exception as e:
            print(f"[Bass] Failed to close damper: {e}")

    def pick_string_with_currentProcessing(self, note_name, octave, damper_stream, fret_stream, timeout=2.0):
        self.estop.require_safe()
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

    def calibrateServo(self):
        self.estop.require_safe()
        for servo in self.servos:
            servo.set_angle(0)
            time.sleep(1)
            servo.set_angle(90)
            time.sleep(1)
            servo.set_angle(0)
            time.sleep(1)
            print(servo)
        print("[Bass] Servos calibrated.")

    def pickString(self, servo, delay_between_picks):
        self.estop.require_safe()
        print(f"[Bass] Setting all servos except {servo.name} to zero position.")
        # for s in self.servos:
        #     if s != servo:
        #         s.hold()
        print(f"[Bass] Picking string {servo.name}")
        servo.pick()
        time.sleep(delay_between_picks)
   
    def pickingTest(self, servos, delay_between_picks):
        self.estop.require_safe()
        for servo in servos:
            print(f"[Bass] Picking string {servo.name}")
            self.pickString(servo, delay_between_picks)
            time.sleep(delay_between_picks)

    def frettingTest(self, fret_objects, delay_between_frets):
        self.estop.require_safe()
        if not isinstance(fret_objects, list):
            fret_objects = [fret_objects]
        for fret in fret_objects:
            if fret in self.frets:
                print(f"[Bass] Activating fret {fret}")
                fret.on()
                time.sleep(delay_between_frets)
                fret.off()
                time.sleep(delay_between_frets)
            else:
                print(f"[Bass] Warning: {fret} is not a valid fret object.")
                
    def dampingTest(self, damper, delay_between_damps):
                    self.estop.require_safe()
                    print(f"[Bass] Activating damper {damper}")
                    damper.on()
                    time.sleep(delay_between_damps)
                    damper.off()
                    time.sleep(delay_between_damps)
        