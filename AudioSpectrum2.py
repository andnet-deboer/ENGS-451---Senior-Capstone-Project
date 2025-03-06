import pyaudio
import numpy as np
import matplotlib.pyplot as plt
import time
import threading
from matplotlib.widgets import Slider

# Constants
CHUNK = 512  # Smaller chunk for higher FPS
FORMAT = pyaudio.paInt16
CHANNELS = 1
RATE = 44100

# Initialize PyAudio
p = pyaudio.PyAudio()
stream = p.open(format=FORMAT, channels=CHANNELS, rate=RATE, input=True, output=False, frames_per_buffer=CHUNK)

# Frequency axis for FFT
xf = np.fft.rfftfreq(CHUNK, 1 / RATE)

# Matplotlib setup
fig, (ax1, ax2) = plt.subplots(2, figsize=(10, 5))
line, = ax1.plot(np.arange(CHUNK), np.zeros(CHUNK), '-', lw=1)
line_fft, = ax2.semilogx(xf, np.zeros(len(xf)), '-', lw=1)
ax1.set_ylim(-3000, 3000)
ax2.set_xlim(20, RATE / 2)

# Sensitivity slider
ax_slider = plt.axes([0.25, 0.02, 0.65, 0.03])
sensitivity_slider = Slider(ax_slider, 'Sensitivity', 100, 2000, valinit=500)
sensitivity = 500

def update_sensitivity(val):
    global sensitivity
    sensitivity = sensitivity_slider.val
sensitivity_slider.on_changed(update_sensitivity)

# Variables for real-time processing
frame_count = 0
start_time = time.time()
running = True

def audio_stream():
    global frame_count, running
    while running:
        data = stream.read(CHUNK, exception_on_overflow=False)
        data_np = np.frombuffer(data, dtype=np.int16)
        
        # Compute FFT efficiently
        yf = np.abs(np.fft.rfft(data_np)) / CHUNK
        
        # Update plots
        line.set_ydata(data_np)
        line_fft.set_ydata(yf)
        
        if np.max(np.abs(data_np)) > sensitivity:
            ax1.set_facecolor('lightgreen')  # Signal detected
        else:
            ax1.set_facecolor('white')
        
        frame_count += 1
        
        if frame_count % 5 == 0:  # Update UI every 5 frames for efficiency
            try:
                fig.canvas.draw()
                fig.canvas.flush_events()
            except:
                break

# Run audio stream in a separate thread
thread = threading.Thread(target=audio_stream, daemon=True)
thread.start()
plt.show()

# Cleanup on close
running = False
thread.join()
stream.stop_stream()
stream.close()
p.terminate()

# Print performance stats
fps = frame_count / (time.time() - start_time)
print(f'Average FPS: {fps:.1f}')
