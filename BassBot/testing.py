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
    bass.pickString(bass.servoG, delay)
    bass.pickString(bass.servoD, delay)
    bass.pickString(bass.servoA, delay)   
    bass.pickString(bass.servoE, delay)

    





try:
   # while music_thread.is_alive():
    while True:
        
       #bass.frettingTest(bass.damper, 2)S
       #bass.dampingTest(bass.damper,2)
       #bass.frettingTest(bass.fret3,1)
    #    for i in range(1,5):
    #     bass.damp_bass(bass.servoE)
    #     for j in range(1,100):
    #        time.sleep(1)
    #        bass.fret3.on()
    #        time.sleep(0.1)
    #        bass.servoE.pick()
    #        time.sleep(2)
    #        bass.fret3.off()
           
    #     time.sleep(100)
    #    for i in range(1,5):
    #     bass.servoA.pick()
    #     time.sleep(0.1)
       for i in range(1,10):
        bass.servoA.sustain()
        time.sleep(0.2) 
       for i in range(1,10):
        bass.servoD.sustain()
        time.sleep(0.2)
      #FourStringPickSequence(1)
        ##    # time.sleep(1
#
        #bass.pickString(bass.servoG, 1)
        #bass.servoA.sustain()
        #time.sleep(1)
   #

        #    # time.sleep(1)
        #bass.pickString(bass.servoA, 1)
        #time.sleep(0.5)
        #bass.pickString(bass.servoG,1)
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
