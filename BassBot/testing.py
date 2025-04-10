import os
import time
import threading
from collections import deque
from datetime import datetime

from bass import Bass
from composer import Composer
from score_parser import ScoreParser


# === Initialize Hardware ===
bass = Bass()



# === Load and Parse Score ===
music_file = "7NationArmy.xml"  # Replace with your MusicXML file
parser = ScoreParser(music_file)
note_matrix = parser.generate_note_matrix()



# === Playback Thread ===
def play_song():
    print("[System] Starting song performance...\n")
    #composer.pick_string_test(bass.servoA, bass.fret4, num_picks=500,delay_between=2)
    #bass.zero_servos()
    #bass.pick_string("A", 4, damper_stream, fret_stream)
    #bass.pick_string("A", 4, damper_stream, fret_stream)
   # Composer.play()
    print("\n[System] Song complete.")
    #bass.bass_off()
def FourStringPickSequence(delay=1):
    bass.pickString(bass.servoE, delay)
    bass.pickString(bass.servoA, delay)   
    bass.pickString(bass.servoD, delay)
    bass.pickString(bass.servoG, delay)

# === Run ===
music_thread = threading.Thread(target=play_song, daemon=True)
music_thread.start()

try:
   # while music_thread.is_alive():
    while True:
        
       bass.frettingTest(bass.fret3, 2)
        #FourStringPickSequence(0.2)
        #    # time.sleep(1)
            # bass.pickString(bass.servoE,1 )
        #    # time.sleep(1)
        #     bass.pickString(bass.servoD, 0.2)
        #     #time.sleep(1)
        #     bass.pickString(bass.servoG, 0.2)
        # time.sleep(1)
            #bass.pickString(bass.servoG, 1)
        # time.sleep(0.2)
            #bass.zero_servos

except KeyboardInterrupt:
    print("\n[System] Interrupted by user.")

finally:
    
    bass.bass_off()
   # stop_logging(threads, file_handle)
    print("[System] Shutdown complete.")
