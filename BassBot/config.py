
# Servo GPIO pins
SERVO_PINS = {
    'E': 24,
    'A': 18,
    'D': 27,
    'G': 10
}

# Relay numbers (logical mapping)
RELAY_NUMBERS = {
    'fret1': 3,
    'fret2': 1,
    'fret3': 4,
    'fret4': 2,
    'damper': 5
}

# Sensor I2C Addresses
SENSOR_ADDRESSES = {
    'FRET': 0x44,
    'DAMPER': 0x41,
    'PICK': 0x40
}

# Pick detection threshold in mA
CURRENT_THRESHOLD = 2000

# Delay after pick to allow servo to complete motion
DELAY_AFTER_PICK = 0.3

# Max size for current deque
CURRENT_STREAM_SIZE = 20

# Directory for logs
LOG_DIR = "LogFiles"
