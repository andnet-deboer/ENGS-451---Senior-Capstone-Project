import time
import threading
from bass import Bass
from config import NOTE_MAPPING_KEYS
from music21 import converter, instrument, note, chord, stream
from xml.etree import ElementTree as ET
from score_parser import ScoreParser
from datetime import timedelta

playback_row = None
class Composer:
    def __init__(self, note_matrix, bass: Bass, damper_stream=None, fret_stream=None, pause_event=None, stop_event=None):
        self.note_matrix = note_matrix
        self.bass = bass
        self.damper_stream = damper_stream
        self.fret_stream = fret_stream
        self.pause_event = pause_event or threading.Event()
        self.pause_event.set()
        self.stop_event = stop_event or threading.Event()

    def play(self):
        global playback_row
        self.bass.estop.require_safe()
        for i in range(len(self.note_matrix) - 1):
            playback_row = i
            if self.stop_event.is_set():
                print("[Composer] Stop requested. Exiting.")
                self.bass.bass_off()
                return
            self.pause_event.wait()
            row = self.note_matrix[i]
            element_type, label, start_time, end_time, duration = row

            if element_type == "Note":
                note_name = ''.join(filter(str.isalpha, label))
                octave = int(''.join(filter(str.isdigit, label)))

                self.bass.pick_string(
                    note_name=note_name,
                    octave=octave+1,
                    #damper_stream=self.damper_stream,
                    fret_stream=self.fret_stream,
                    duration=duration,
                    dampednote = True
                )

                time.sleep(duration)
                print(f"[Composer] Sleeping for duration: {duration} seconds")

            elif element_type == "Rest":
                time.sleep(duration)
                self.bass.relay_off()

    # def pick_string_test(self, servo, fret=None, num_picks=5, delay_between=0.5):
    #     self.bass.estop.require_safe()
    #     print(f"[Test] Running pick test on servo: {servo.name}, with fret: {fret}, {num_picks} picks")

    #     for i in range(num_picks):
    #         if self.stop_event.is_set():
    #             print("[Composer Test] Stop requested.")
    #             self.bass.bass_off()
    #             return
    #         self.pause_event.wait()
    #         print(f"[Test] Pick {i+1}")
    #         self.bass.damper.on()
    #         time.sleep(0.1)
    #         fret.on()
    #         time.sleep(0.1)
    #         self.bass.damper.off()
    #         time.sleep(0.1)
    #         servo.pick()
    #         time.sleep(0.5)
    #         self.bass.relay_off()

    #     self.bass.bass_off()
    #     print("[Test] Pick test complete.")

    # def dampSequence(self):
    #     self.bass.damper.on()
    #     time.sleep(0.5)
    def play_notes(self, note_matrix):
        #self.bass.start_damping_loop()
        self.bass.estop.require_safe()
        self.bass.zero_servos()
        isdamped = True
        actuator_history = [[None, None], [None, None]]  # [previous, ccommand:~remote.forwardedPorts.focusurrent]
        for i in range(len(note_matrix) - 1):
            if self.stop_event.is_set():
                print("[Composer] Stop requested. Exiting playback.")
                self.bass.bass_off()
                self.bass.cleanup()
                return
            self.pause_event.wait()


            current_row = note_matrix[i]
            next_row = note_matrix[i + 1]

            note = current_row[0]
            nextNote = next_row[0]
            duration = current_row[5]

            if not hasattr(note, "isNote") or not hasattr(note, "isRest"):
                continue

            if note.isRest:
                self.bass.all_relays_off()
                time.sleep(duration)
                # actuator_history = [[None, None], [None, None]]
                continue

            if note.isNote:
                octave = note.octave
                servo, fret = self.bass.note_mapping.get((note.name, octave), (None, None))
                if nextNote.isNote:
                    nextsServo, nextFret = self.bass.note_mapping.get((nextNote.name, nextNote.octave), (None, None))
                previous_servo, previous_fret = actuator_history[0]
                current_servo, current_fret = actuator_history[1]
                
                #FRETTING
                if fret is not None:
                    if previous_fret == current_fret:
                        fretDown = False
                    else:
                        fretDown = True
                        fret.on()
                        print("Fretting: ",fret)
          
                #PICKING
                if (servo is not None):
                    #self.update_active_servo(servo)
                    self.bass.damp_bass(servo)
                    if previous_servo == current_servo:
                        servo.sustain()
                        print("Picking With Sustain: ",note)
                    else:
                        #servo.pick(True)
                        servo.sustain()
                        print("Picking With Damp: ",note)
                    
                time.sleep(duration)
                
                if fret is not None and nextFret != fret:
                    fret.off()
                
                # Update history: current becomes previous, new current is assigned
                actuator_history[0] = actuator_history[1]
                actuator_history[1] = [servo, fret]
        #self.bass.stop_damping_loop()
        self.bass.cleanup()
               
