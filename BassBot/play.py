import os
import time
import threading
from collections import deque
from datetime import datetime

from bass import Bass
from composer import Composer
from score_parser import ScoreParser
from currentLogging import start_logging_multirate, stop_logging
from config import CURRENT_STREAM_SIZE, LOG_DIR

# === Setup Logging Directory ===
os.makedirs(LOG_DIR, exist_ok=True)
timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
log_filename = os.path.join(LOG_DIR, f"ina260_multirate_{timestamp}.csv")

# === Initialize Hardware ===
bass = Bass()

# === Sensor Buffers ===
fret_stream   = deque([0]*CURRENT_STREAM_SIZE, maxlen=CURRENT_STREAM_SIZE)
damper_stream = deque([0]*CURRENT_STREAM_SIZE, maxlen=CURRENT_STREAM_SIZE)
pick_stream   = deque([0]*CURRENT_STREAM_SIZE, maxlen=CURRENT_STREAM_SIZE)

# === Start Multithreaded Logging ===
threads, file_handle = start_logging_multirate(
    filename=log_filename,
    fret_current_stream=fret_stream,
    damper_current_stream=damper_stream,
    pick_current_stream=pick_stream
)

# === Load and Parse Score ===
music_file = "7NationArmy.xml"  # Replace with your MusicXML file
parser = ScoreParser(music_file)
note_matrix = parser.generate_note_matrix()

# === Initialize Composer ===
composer = Composer(
    note_matrix=note_matrix,
    bass=bass,
    damper_stream=damper_stream,
    fret_stream=fret_stream
)

# === Playback Thread ===
def play_song():
    print("[System] Starting song performance...\n")
    #composer.pick_string_test(bass.servoA, bass.fret4, num_picks=500,delay_between=2)
    composer.play()
    print("\n[System] Song complete.")
    #bass.bass_off()

# === Run ===
music_thread = threading.Thread(target=play_song, daemon=True)
music_thread.start()

try:
    while music_thread.is_alive():
        time.sleep(0.5)
        #bass.zero_servos

except KeyboardInterrupt:
    print("\n[System] Interrupted by user.")

finally:
    bass.bass_off()
    stop_logging(threads, file_handle)
    print(f"[System] Data saved to: {log_filename}")
    print("[System] Shutdown complete.")
