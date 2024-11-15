import time
from flask import Flask, render_template
from flask_socketio import SocketIO
from threading import Thread

# Flask setup
app = Flask(__name__)
socketio = SocketIO(app)

# Task 1: Send the current time every second
def send_time():
    while True:
        current_time = time.strftime('%H:%M:%S')
        
        # Emit the current time to the client
        socketio.emit('update_time', {'time': current_time})

        # Emit progress (simulating time as a loading bar)
        socketio.emit('update_progress', {'task': 'time', 'progress': 100})
        
        time.sleep(1)

# Task 2: Simulate a counting task independent of time
def count_numbers():
    count = 1
    while True:
        # Emitting count updates
        socketio.emit('update_count', {'count': count})

        # Emitting progress for the counting task
        socketio.emit('update_progress', {'task': 'count', 'progress': (count % 100)})
        
        # Increment count and wrap around after 100
        count = count + 1 if count < 100 else 1
        
        time.sleep(1)

# Route to render the HTML page
@app.route('/')
def index():
    return render_template('index.html')

# Start the time sending and counting functions in separate threads
if __name__ == '__main__':
    # Start the threads for sending time and counting numbers
    time_thread = Thread(target=send_time)
    time_thread.daemon = True
    time_thread.start()

    count_thread = Thread(target=count_numbers)
    count_thread.daemon = True
    count_thread.start()

    # Run the Flask web server
    socketio.run(app, host='0.0.0.0', port=5000)
