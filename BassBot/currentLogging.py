import os
import time
import threading
from collections import deque
from datetime import datetime
import board
import adafruit_ina260


class CurrentSensor:
    def __init__(self, address):
        self.i2c = board.I2C()
        self.ina260 = adafruit_ina260.INA260(self.i2c, address=address)

    def current(self):
        return self.ina260.current

    def voltage(self):
        return self.ina260.voltage

    def power(self):
        return self.ina260.power


def log_sensor_values(sensor, label, rate, start_time, data_dict, data_lock, current_stream=None):
    period = 1.0 / rate
    while logging_active:
        loop_start = time.time()
        try:
            t = loop_start - start_time
            current = sensor.current()
            voltage = sensor.voltage()

            with data_lock:
                data_dict[label] = (t, current, voltage)
            if current_stream is not None:
                current_stream.append(current)
        except Exception as e:
            print(f"[{label} ERROR] {e}")

        elapsed = time.time() - loop_start
        sleep_time = period - elapsed
        if sleep_time > 0:
            time.sleep(sleep_time)


def start_logging_multirate(filename="ina260_multicolumn.csv", fret_current_stream=None):
    fret_sensor = CurrentSensor(0x44)
    damper_sensor = CurrentSensor(0x41)
    servo_sensor = CurrentSensor(0x40)

    global logging_active
    logging_active = True
    start = time.time()

    data_lock = threading.Lock()
    sensor_data = {}

    file_handle = open(filename, "w")
    file_handle.write("Time(s),Fret_Current(mA),Fret_Voltage(V),Damper_Current(mA),Damper_Voltage(V),Pick_Current(mA),Pick_Voltage(V)\n")

    def csv_writer():
        while logging_active:
            with data_lock:
                fret = sensor_data.get("FRET", (None, None, None))
                damper = sensor_data.get("DAMPER", (None, None, None))
                pick = sensor_data.get("PICK", (None, None, None))
                t = time.time() - start
                line = f"{t:.3f}," \
                       f"{fret[1] if fret[1] else ''},{fret[2] if fret[2] else ''}," \
                       f"{damper[1] if damper[1] else ''},{damper[2] if damper[2] else ''}," \
                       f"{pick[1] if pick[1] else ''},{pick[2] if pick[2] else ''}\n"
                file_handle.write(line)
                file_handle.flush()
            time.sleep(0.01)

    threads = [
        threading.Thread(target=log_sensor_values, args=(fret_sensor, "FRET", 100, start, sensor_data, data_lock, fret_current_stream)),
        threading.Thread(target=log_sensor_values, args=(damper_sensor, "DAMPER", 100, start, sensor_data, data_lock)),
        threading.Thread(target=log_sensor_values, args=(servo_sensor, "PICK", 20, start, sensor_data, data_lock)),
        threading.Thread(target=csv_writer)
    ]

    for t in threads:
        t.start()

    return threads, file_handle


def stop_logging(threads, file_handle):
    global logging_active
    logging_active = False
    for t in threads:
        t.join()
    file_handle.close()
    print("Logging stopped and file saved.")
