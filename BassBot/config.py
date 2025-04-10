# Servo GPIO pins
SERVO_PINS = {
    'E': 10,
    'A': 27,
    'D': 24,
    'G': 18,
}

# EStop GPIO pin
ESTOP_PIN = 26

# Relay numbers (logical mapping)
RELAY_NUMBERS = {
    'fret1': 1,
    'fret2': 2,
    'fret3': 4,
    'fret4': 3,
    'damper': 5,
}

# Sensor I2C Addresses
SENSOR_ADDRESSES = {
    'FRET': 0x44,
    'DAMPER': 0x41,
    'PICK': 0x40
}

NOTE_MAPPING_KEYS = {
    ('E', 2): ('E', None),
    ('F', 2): ('E', 'fret1'),
    ('F#', 2): ('E', 'fret2'),
    ('G', 2): ('E', 'fret3'),
    ('G#', 2): ('E', 'fret4'),
    ('A', 2): ('A', None),
    ('A#', 2): ('A', 'fret1'),
    ('B', 2): ('A', 'fret2'),
    ('C', 3): ('A', 'fret3'),
    ('C#', 3): ('A', 'fret4'),
    ('D', 3): ('D', None),
    ('D#', 3): ('D', 'fret1'),
    ('E', 3): ('D', 'fret2'),
    ('F', 3): ('D', 'fret3'),
    ('F#', 3): ('D', 'fret4'),
    ('G', 3): ('G', None),
    ('G#', 3): ('G', 'fret1'),
    ('A', 3): ('G', 'fret2'),
    ('A#', 3): ('G', 'fret3'),
    ('B', 3): ('G', 'fret4'),
}


# Current thresholds (in mA)
CURRENT_THRESHOLD = 2000         # General use (fallback/default)
DAMP_THRESHOLD = 2000            # Minimum to detect damper pressed
FRET_THRESHOLD = 3000            # Minimum to detect fret pressed
RELEASE_THRESHOLD = 400          # Threshold below which damper is considered released

# Timing
DELAY_AFTER_PICK = 0.1           # Allow servo motion to complete after pick

# Stream settings
CURRENT_STREAM_SIZE = 20

# Log settings
LOG_DIR = "LogFiles"
