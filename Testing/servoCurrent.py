# SPDX-FileCopyrightText: 2021 ladyada for Adafruit Industries
# SPDX-License-Identifier: MIT

import time
import board
import adafruit_ina260
import matplotlib.pyplot as plt
import matplotlib.animation as animation

# Initialize the sensor
i2c = board.I2C()  # uses board.SCL and board.SDA
# i2c = board.STEMMA_I2C()  # For using the built-in STEMMA QT connector on a microcontroller
ina260 = adafruit_ina260.INA260(i2c)

# Initialize lists to store data
times = []
currents = []
voltages = []

# Create a figure and axis for the plot
fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(15, 10))

# Create a line object with random data
line_current, = ax1.plot([], [], '-', lw=2, label='Current (mA)', color='blue')
line_voltage, = ax2.plot([], [], '-', lw=2, label='Voltage (V)', color='green')

# Format waveform axes
ax1.set_title('INA260 Sensor Readings')
ax1.set_xlabel('Time (s)')
ax1.set_ylabel('Current (mA)')
ax1.legend(loc='upper right')
ax1.set_xlim(0, 10)
ax1.set_ylim(0, 5000)

ax2.set_xlabel('Time (s)')
ax2.set_ylabel('Voltage (V)')
ax2.legend(loc='upper right')
ax2.set_xlim(0, 10)
ax2.set_ylim(0, 20)

print('stream started')

# for measuring frame rate
frame_count = 0
start_time = time.time()

def animate(i):
    global times, currents, voltages

    # Read sensor data
    current = ina260.current
    voltage = ina260.voltage
    current_time = time.time() - start_time

    # Append data to lists
    times.append(current_time)
    currents.append(current)
    voltages.append(voltage)

    # Limit lists to the last 100 data points
    times = times[-100:]
    currents = currents[-100:]
    voltages = voltages[-100:]

    # Update line data
    line_current.set_data(times, currents)
    line_voltage.set_data(times, voltages)

    # Update axes limits
    ax1.set_xlim(max(0, current_time - 10), current_time)
    ax2.set_xlim(max(0, current_time - 10), current_time)

# Create an animation that updates the plot every 100 milliseconds
ani = animation.FuncAnimation(fig, animate, interval=100)

# Show the plot
plt.tight_layout()
plt.show()

try:
    while True:
        current = ina260.current
        voltage = ina260.voltage
        power = ina260.power
        current_time = time.time() - start_time

        # Append data to lists
        times.append(current_time)
        currents.append(current)
        voltages.append(voltage)

        print(
            "Current: %.2f mA Voltage: %.2f V Power:%.2f mW"
            % (current, voltage, power)
        )
        
        time.sleep(1)

except KeyboardInterrupt:
    print("Program stopped by user. Saving data to file...")

    # Save data to a text file
    with open("ina260_data.csv", "w") as f:
        f.write("Time(s),Current(mA),Voltage(V)\n")
        for t, c, v in zip(times, currents, voltages):
            f.write(f"{t},{c},{v}\n")

    print("Data saved to ina260_data.csv")