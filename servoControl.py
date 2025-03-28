import time
import numpy as np
import matplotlib.pyplot as plt
from gpiozero import Servo
from gpiozero.pins.pigpio import PiGPIOFactory

# Create the PiGPIOFactory instance for using pigpio
factory = PiGPIOFactory()

class ServoWithControl:
    def __init__(self, pin, min_angle=-90, max_angle=90, pin_factory=None):
        self.servo = Servo(pin, pin_factory=pin_factory)
        self.min_angle = min_angle
        self.max_angle = max_angle
        self.current_value = 0  # Current servo position as a value between -1 and 1
        self.target_value = 0
        self.velocity_rpm = 0  # The current speed of the servo in RPM

        # For plotting
        self.positions = []
        self.velocities = []
        self.times = []

    def set_position(self, angle):
        """
        Set the servo to a specific angle.
        The angle is expected to be between min_angle and max_angle.
        """
        if angle < self.min_angle:
            angle = self.min_angle
        elif angle > self.max_angle:
            angle = self.max_angle
        
        # Convert angle to a servo value (-1 to 1)
        value = max(-90, min(90, angle))
        self.servo.value = value

    def move_to(self, target_angle, velocity_bpm):
        """
        Move the servo to a target angle at a constant speed (BPM).
        """
        # Convert BPM to RPM
        velocity_rpm = velocity_bpm / 180
        
        # Set the target position
        self.target_value = max(self.min_angle, min(self.max_angle, target_angle))
        
        # Set the velocity in RPM (Revolutions per minute)
        self.velocity_rpm = velocity_rpm
        
        # Move the servo at the specified velocity
        self._move_with_constant_velocity()

    def _move_with_constant_velocity(self):
        """
        Move the servo to the target value at a constant velocity.
        """
        # Convert RPM to degrees per second
        degrees_per_minute = 360 * self.velocity_rpm  # Total degrees per minute
        degrees_per_second = degrees_per_minute / 60  # Degrees per second
        
        # Calculate the total distance to move
        distance_to_move = abs(self.target_value - self.current_value)
        
        # Calculate time required to move to the target at the given velocity
        time_to_move = distance_to_move / degrees_per_second

        # Determine the direction of movement (1 for positive direction, -1 for negative)
        direction = 1 if self.target_value > self.current_value else -1

        # Record start time for timing the motion
        start_time = time.time()

        while abs(self.current_value - self.target_value) > 0.5:  # Allow for small error tolerance
            # Move the servo
            self.current_value += degrees_per_second * direction * 0.05  # Update every 0.05 seconds

            # Clip the position to ensure it's within the allowed range
            self.current_value = max(self.min_angle, min(self.max_angle, self.current_value))

            # Set the servo position
            self.servo.value = self.current_value

            # Record data for plotting
            current_time = time.time() - start_time
            self.times.append(current_time)
            self.positions.append(self.current_value)
            self.velocities.append(self.velocity_rpm)

            # Print debug info
            print(f"Target: {self.target_value:.2f}, Current: {self.current_value:.2f}, Velocity: {self.velocity_rpm} RPM")

            # Delay to simulate time taken for movement
            time.sleep(0.05)  # Update every 50ms for smooth motion

        # Final confirmation
        print(f"Target reached: {self.target_value:.2f}, Current: {self.current_value:.2f}")

    def stop(self):
        """ Stop the servo by setting its value to None (uncontrolled). """
        self.servo.detach()

    def plot_data(self):
        """ Plot the servo position, velocity, and time over time. """
        plt.figure(figsize=(10, 6))

        # Plot Position
        plt.subplot(3, 1, 1)
        plt.plot(self.times, self.positions, label='Position (Servo Value)', color='blue')
        plt.xlabel('Time (s)')
        plt.ylabel('Position (Value)')
        plt.title('Servo Position Over Time')

        # Plot Velocity
        plt.subplot(3, 1, 2)
        plt.plot(self.times, self.velocities, label='Velocity (RPM)', color='green')
        plt.xlabel('Time (s)')
        plt.ylabel('Velocity (RPM)')
        plt.title('Servo Velocity Over Time')

        plt.tight_layout()
        plt.show()

try:
    servoG_control = ServoWithControl(18, min_angle=-10, max_angle=10, pin_factory=factory)
    #servoG_control = ServoWithControl(27, min_angle=-10, max_angle=10, pin_factory=factory)
    #servoG_control = ServoWithControl(10, min_angle=--10, max_angle=10, pin_factory=factory)
    #servoG_control = ServoWithControl(24, min_angle=-10, max_angle=10, pin_factory=factory)
    for _ in range(3000):  # Repeat the motion 3 times
        servoG_control.move_to(-1, velocity_bpm=120)  # Move to -0.3 degrees at 60 BPM
        time.sleep(0.2)
        servoG_control.move_to(1, velocity_bpm=120)  # Move to 0.3 degrees at 60 BPM
        time.sleep(0.2)
    # After the movement is complete, plot the data
    servoG_control.stop()
    servoG_control.plot_data()
except KeyboardInterrupt:
    print("Program stopped")
    servoG_control.stop()