import time
import threading
from bass import Bass
from config import NOTE_MAPPING_KEYS
from music21 import converter, instrument, note, chord, stream
from xml.etree import ElementTree as ET
from score_parser import ScoreParser
from datetime import timedelta

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
        self.bass.estop.require_safe()
        for i in range(len(self.note_matrix) - 1):
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
                    damper_stream=self.damper_stream,
                    fret_stream=self.fret_stream,
                    duration=duration
                )

                time.sleep(duration)
                print(f"[Composer] Sleeping for duration: {duration} seconds")

            elif element_type == "Rest":
                time.sleep(duration)
                self.bass.relay_off()

    def pick_string_test(self, servo, fret=None, num_picks=5, delay_between=0.5):
        self.bass.estop.require_safe()
        print(f"[Test] Running pick test on servo: {servo.name}, with fret: {fret}, {num_picks} picks")

        for i in range(num_picks):
            if self.stop_event.is_set():
                print("[Composer Test] Stop requested.")
                self.bass.bass_off()
                return
            self.pause_event.wait()
            print(f"[Test] Pick {i+1}")
            self.bass.damper.on()
            time.sleep(0.1)
            fret.on()
            time.sleep(0.1)
            self.bass.damper.off()
            time.sleep(0.1)
            servo.pick()
            time.sleep(0.5)
            self.bass.relay_off()

        self.bass.bass_off()
        print("[Test] Pick test complete.")

    def dampSequence(self):
        self.bass.damper.on()
        time.sleep(0.5)

    def play_notes(self, note_matrix):
        self.bass.estop.require_safe()
        self.bass.zero_servos()
        for i in range(len(note_matrix) - 1):
            if self.stop_event.is_set():
                print("[Composer] Stop requested. Exiting playback.")
                self.bass.bass_off()
                return
            self.pause_event.wait()

            current_row = note_matrix[i]
            next_row = note_matrix[i + 1]

            note = current_row[0]
            duration = current_row[5]

            if not hasattr(note, "isNote") or not hasattr(note, "isRest"):
                continue

            if note.isRest:
                time.sleep(duration)
                self.bass.all_relays_off()
                continue

            if note.isNote:
                octave = note.octave
                servo, fret = self.bass.note_mapping.get((note.name, octave), (None, None))
                self.bass.all_relays_off()
                if fret:
                    fret.on()
                if servo:
                    servo.pick()
                time.sleep(duration)
