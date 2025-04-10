import time
from bass import Bass
from config import NOTE_MAPPING_KEYS
from music21 import converter, instrument, note, chord, stream
from xml.etree import ElementTree as ET
from score_parser import ScoreParser
from datetime import timedelta
class Composer:
    def __init__(self, note_matrix, bass: Bass, damper_stream, fret_stream):
        self.note_matrix = note_matrix
        self.bass = bass
        self.damper_stream = damper_stream
        self.fret_stream = fret_stream

    def play(self):
        self.bass.estop.require_safe()
        """
        Iterate through the note matrix and trigger the full pick_string logic
        for each note using sensor-based control.
        """
        for i in range(len(self.note_matrix) - 1):
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
            print(f"[Test] Pick {i+1}")
            
            # 1. Dampen
            self.bass.damper.on()
            print("[Test] Damper ON")
            
            time.sleep(0.1)  # Give time for damper contact

            # 2. Fret
      
            fret.on()
            print("[Test] Fret ON")

            # 3. Undampen
            time.sleep(0.1)
            self.bass.damper.off()
            print("[Test] Damper OFF")

            time.sleep(0.1)  # Time for damper to lift

            # 4. Pick
            servo.pick()
            time.sleep(0.5)

            # # 5. Damp
            # self.bass.damper.on()
            # print("[Test] Damper ON")
            
            # time.sleep(0.1)  # Give time for damper contact

            # 6. Unfret (if provided)

            self.bass.relay_off()
     

        self.bass.bass_off()
        print("[Test] Pick test complete.")
   
    def dampSequence(self):
        self.bass.damper.on()
        time.sleep(0.5)

    def play_notes(self, note_matrix):
        self.bass.estop.require_safe()
        self.bass.zero_servos()
        #self.dampSequence()
        for i in range(len(note_matrix) - 1):  # Iterate up to the second-to-last row
            current_row = note_matrix[i]
            next_row = note_matrix[i + 1]

            note = current_row[0]

            # Keep your original duration logic
            duration = current_row[5]
          
            # Process only music21 Notes or Rests
            if not hasattr(note, "isNote") or not hasattr(note, "isRest"):
                continue

            # Handle rests
            if note.isRest:
                time.sleep(duration)
                self.bass.all_relays_off()
                continue

            # Handle notes
            if note.isNote:
                octave = note.octave 
                servo, fret = self.bass.note_mapping.get((note.name, octave), (None, None))

                self.bass.all_relays_off()

                if fret:
                    fret.on()

                if servo:
                    servo.pick()

                time.sleep(duration)
