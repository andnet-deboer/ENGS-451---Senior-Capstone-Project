from pathlib import Path
from datetime import datetime
import csv, threading, time, os
from collections import deque

import board
import adafruit_ina260
from matplotlib.figure import Figure

# pull your I2C addresses from config
from config import SENSOR_ADDRESSES

class INA260:
    def __init__(self, i2c, address):
        self._dev = adafruit_ina260.INA260(i2c, address=address)
    @property
    def current(self): return self._dev.current
    @property
    def voltage(self): return self._dev.voltage
    @property
    def power(self):   return self._dev.power

class CurrentLogger:
    def __init__(self, interval=0.2, history_seconds=60):
        # ensure output dir exists
        Path("LogFiles").mkdir(exist_ok=True)

        self.interval = float(interval)
        self.history  = int(history_seconds / interval)
        self.i2c      = board.I2C()
        # instantiate sensors
        self.sensors = {n: INA260(self.i2c,a)
                        for n,a in SENSOR_ADDRESSES.items()}

        # open CSV under LogFiles/
        ts = datetime.now().strftime("%Y%m%d_%H%M%S")
        self.csv_path = Path("LogFiles")/f"ina260_log_{ts}.csv"
        self._fh = self.csv_path.open("w", newline="")
        self._wr = csv.writer(self._fh)
        header = ["elapsed_s"] + [f"{n}_mA" for n in self.sensors] + [f"{n}_V" for n in self.sensors]
        self._wr.writerow(header)
        self._fh.flush()

        # in-memory buffers for live plotting
        self._times = deque(maxlen=self.history)
        self._buf   = {n:deque(maxlen=self.history) for n in self.sensors}

        # thread control
        self._stop = threading.Event()
        self._thr  = threading.Thread(target=self._worker, daemon=True)

    def start(self):
        self._thr.start()
    def stop(self):
        self._stop.set(); self._thr.join(); self._fh.close()

    def _worker(self):
        # optional: pin this thread to core 1
        try:
            os.sched_setaffinity(0, {1})
        except Exception:
            pass
        t0 = time.time()
        while not self._stop.is_set():
            now = time.time() - t0
            row = [f"{now:.3f}"]
            for n,s in self.sensors.items():
                c = s.current; v = s.voltage
                row += [f"{c:.2f}", f"{v:.2f}"]
                self._buf[n].append(c)
            self._times.append(now)
            self._wr.writerow(row); self._fh.flush()
            time.sleep(self.interval)