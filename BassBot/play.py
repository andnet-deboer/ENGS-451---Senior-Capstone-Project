#!/usr/bin/env python3
# bass_player.py

import os
import time
import threading
from datetime import datetime

from bass import Bass
from composer import Composer
from score_parser import ScoreParser
from config import LOG_DIR, SENSOR_ADDRESSES
from estop import EStopMonitor
from currentLogger import CurrentLogger  


class BassPlayer:
    def __init__(self,
                 music_file: str,
                 pause_event=None,
                 stop_event=None,
                 log_function=None,
                 estop_callback=None):
        self.music_file    = music_file
        self.pause_event   = pause_event or threading.Event()
        self.stop_event    = stop_event  or threading.Event()
        self.pause_event.set()  # start unpaused

        self.log_function   = log_function
        self.estop_callback = estop_callback

        # === Prepare log directory and filenames ===
        os.makedirs(LOG_DIR, exist_ok=True)
        ts = datetime.now().strftime("%Y%m%d_%H%M%S")
        self.log_filename = os.path.join(LOG_DIR, f"ina260_multirate_{ts}.csv")

        # This list collects text messages (errors, E-STOPS, etc.)
        self.log = []

        # === Hardware and parser/composer setup ===
        self.bass         = Bass()
        self.parser       = ScoreParser(self.music_file)
        self.note_matrix  = self.parser.generate_note_matrix(0)
        self.parser.save_note_matrix(
            os.path.join(LOG_DIR, f"note_matrix_{ts}.csv")
        )

        self.composer           = Composer(note_matrix=self.note_matrix, bass=self.bass)
        self.composer.pause_event = self.pause_event
        self.composer.stop_event  = self.stop_event

        # === Threads ===
        self.music_thread   = threading.Thread(target=self.play_song, daemon=True)
        self.estop_monitor  = EStopMonitor()
        self.watcher_thread = threading.Thread(target=self.estop_watcher, daemon=True)

        # === Current logger ===
     
        self.current_logger = CurrentLogger(
            interval=0.001,        # 1000 Hz sampling
            history_seconds=60     # scrolling window
        )

    def play_song(self):
        print("[System] Starting song performance…")
        try:
            self.composer.play_notes(self.note_matrix)
            print("[System] Song complete.")
            self.log.append("Playback finished.")
        except RuntimeError as e:
            print(f"[E-STOP] {e}")
            self.bass.bass_off()
            self.log.append(f"E-STOP during playback: {e}")
        except Exception as e:
            print(f"[ERROR] Unexpected error: {e}")
            self.bass.bass_off()
            self.log.append(f"Playback error: {e}")

    def estop_watcher(self):
        triggered = False
        while self.music_thread.is_alive():
            if self.estop_monitor.is_triggered() and not triggered:
                print("\n[E-STOP] Emergency Stop Triggered! Shutting down…")
                self.log.append("Emergency stop triggered.")
                self.bass.bass_off()
                self.stop_event.set()
                triggered = True
            time.sleep(0.1)

    def run(self):
        # Start current logging & live plot
        print(f"[System] Logging INA260 data to {self.log_filename}")
        self.current_logger.start()

        # Start music and watcher
        self.music_thread.start()
        self.watcher_thread.start()

        try:
            # Main loop waits for music to finish or stop_event
            while self.music_thread.is_alive():
                if self.stop_event.is_set():
                    print("[BassPlayer] Stop requested. Terminating playback.")
                    self.bass.bass_off()
                    break
                time.sleep(0.5)

        except KeyboardInterrupt:
            print("\n[System] Interrupted by user.")
            self.log.append("Interrupted by KeyboardInterrupt.")
        finally:
            # Clean‑up
            self.bass.bass_off()
            self.current_logger.stop()
            print(f"[System] INA260 log saved to: {self.current_logger.csv_path}")
            print(f"[System] Messages log: {self.log_filename.replace('.csv','_msgs.txt')}")
            # Save textual messages
            with open(self.log_filename.replace('.csv','_msgs.txt'), 'w') as fh:
                for line in self.log:
                    fh.write(line + "\n")
            print("[System] Shutdown complete.")


if __name__ == "__main__":
    player = BassPlayer(music_file="7NationArmy.xml")
    player.run()
