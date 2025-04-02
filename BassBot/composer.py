import time
from bass import Bass
class Composer:
    def __init__(self, note_matrix, bass: Bass, damper_stream, fret_stream):
        self.note_matrix = note_matrix
        self.bass = bass
        self.damper_stream = damper_stream
        self.fret_stream = fret_stream

    def play(self):
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
