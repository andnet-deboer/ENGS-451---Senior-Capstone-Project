import os
import time
import threading
from datetime import datetime

from bass import Bass
from composer import Composer
from score_parser import ScoreParser
from config import CURRENT_STREAM_SIZE, LOG_DIR
from estop import EStopMonitor

class BassPlayer:
    def __init__(self, music_file: str, pause_event=None, stop_event=None, log=None):
        self.music_file = music_file
        self.pause_event = pause_event or threading.Event()
        self.stop_event = stop_event or threading.Event()
        self.pause_event.set()  # Start unpaused
        self.log = log  # Injected from Flask

        # === Setup Logging ===
        os.makedirs(LOG_DIR, exist_ok=True)
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        self.log_filename = os.path.join(LOG_DIR, f"ina260_multirate_{timestamp}.csv")

        # === Initialize Hardware ===
        self.bass = Bass()

        # === Parse Score ===
        self.parser = ScoreParser(self.music_file)
        self.note_matrix = self.parser.generate_note_matrix(1)
        self.parser.save_note_matrix("note_matrix.csv")

        # === Initialize Composer ===
        self.composer = Composer(note_matrix=self.note_matrix, bass=self.bass)
        self.composer.pause_event = self.pause_event
        self.composer.stop_event = self.stop_event

        # === Threads ===
        self.music_thread = threading.Thread(target=self.play_song, daemon=True)
        self.estop_monitor = EStopMonitor()
        self.watcher_thread = threading.Thread(target=self.estop_watcher, daemon=True)

    def play_song(self):
        print("[System] Starting song performance...\n")
        try:
            self.composer.play_notes(self.note_matrix)
            print("[System] Song complete.")
        except RuntimeError as e:
            print(f"[E-STOP] {e}")
            self.bass.bass_off()
            if self.log is not None:
                self.log.append(f"🚨 {str(e)}")
        except Exception as e:
            print(f"[ERROR] Unexpected error: {e}")
            self.bass.bass_off()
            if self.log is not None:
                self.log.append(f"❌ Playback error: {str(e)}")

    def estop_watcher(self):
        triggered = False
        while self.music_thread.is_alive():
            if self.estop_monitor.is_triggered():
                if not triggered:
                    print("\n🚨 [E-STOP] Emergency Stop Triggered! Shutting down...")
                    if self.log is not None:
                        self.log.append("🚨 Emergency stop triggered during playback.")
                    self.bass.bass_off()
                    self.stop_event.set()  # force stop
                    triggered = True
            time.sleep(0.1)

    def run(self):
        try:
            self.music_thread.start()
            self.watcher_thread.start()
            while self.music_thread.is_alive():
                if self.stop_event.is_set():
                    print("[BassPlayer] Stop requested. Terminating playback.")
                    self.bass.bass_off()
                    break
                time.sleep(0.5)
        except KeyboardInterrupt:
            print("\n[System] Interrupted by user.")
        finally:
            self.bass.bass_off()
            print(f"[System] Data saved to: {self.log_filename}")
            print("[System] Shutdown complete.")

# === Example Usage ===
if __name__ == "__main__":
    player = BassPlayer(music_file="7NationArmy.xml")
    player.run()