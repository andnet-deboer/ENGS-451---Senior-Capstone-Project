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
        self.velocity = 0  # The current speed of the servo
        self.acceleration = 0.05  # The rate at which velocity increases
        self.max_velocity = 1  # Maximum speed of the servo
        self.min_velocity = -1  # Minimum speed (negative speed)

        # For plotting
        self.positions = []
        self.velocities = []
        self.accelerations = []
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
        value = (angle - self.min_angle) / (self.max_angle - self.min_angle) * 2 - 1
        self.servo.value = value

    def move_to(self, target_angle, velocity=None, acceleration=None):
        """
        Move the servo to a target angle with controlled velocity and acceleration.
        """
        if velocity is not None:
            self.velocity = velocity
        if acceleration is not None:
            self.acceleration = acceleration

        target_value = (target_angle - self.min_angle) / (self.max_angle - self.min_angle) * 2 - 1
        self.target_value = target_value
        
        # Move the servo with acceleration and velocity control
        self._move_with_velocity_control()

    def _move_with_velocity_control(self):
        """
        Internal method that moves the servo from its current position to the target value
        by gradually increasing its velocity (acceleration) until it reaches the target.
        """
        # Start moving
        start_time = time.time()
        while abs(self.target_value - self.current_value) > 0.01:
            if self.target_value > self.current_value:
                self.velocity = min(self.velocity + self.acceleration, self.max_velocity)  # Accelerate
            elif self.target_value < self.current_value:
                self.velocity = max(self.velocity - self.acceleration, self.min_velocity)  # Decelerate
            
            # Move the servo
            if self.target_value > self.current_value:
                self.current_value += self.velocity
            elif self.target_value < self.current_value:
                self.current_value -= self.velocity

            # Update the servo position
            self.servo.value = self.current_value

            # Record data for plotting
            current_time = time.time() - start_time
            self.times.append(current_time)
            self.positions.append(self.current_value)
            self.velocities.append(self.velocity)
            self.accelerations.append(self.acceleration)

            time.sleep(0.05)  # Delay for smooth motion

    def stop(self):
        """ Stop the servo by setting its value to None (uncontrolled). """
        self.servo.value = None

    def set_velocity(self, velocity):
        """ Set the velocity for the servo (how fast it moves). """
        self.velocity = velocity

    def set_acceleration(self, acceleration):
        """ Set the acceleration for the servo (how quickly it ramps up its velocity). """
        self.acceleration = acceleration

    def plot_data(self):
        """ Plot the servo position, velocity, and acceleration over time. """
        plt.figure(figsize=(10, 6))

        # Plot Position
        plt.subplot(3, 1, 1)
        plt.plot(self.times, self.positions, label='Position (Servo Value)', color='blue')
        plt.xlabel('Time (s)')
        plt.ylabel('Position (Value)')
        plt.title('Servo Position Over Time')

        # Plot Velocity
        plt.subplot(3, 1, 2)
        plt.plot(self.times, self.velocities, label='Velocity', color='green')
        plt.xlabel('Time (s)')
        plt.ylabel('Velocity')
        plt.title('Servo Velocity Over Time')

        # Plot Acceleration
        plt.subplot(3, 1, 3)
        plt.plot(self.times, self.accelerations, label='Acceleration', color='red')
        plt.xlabel('Time (s)')
        plt.ylabel('Acceleration')
        plt.title('Servo Acceleration Over Time')

        plt.tight_layout()
        plt.show()

# Example usage:
try:
    servo_control = ServoWithControl(13, min_angle=-90, max_angle=90, pin_factory=factory)

    # Move back and forth between -90 and 90 degrees
    for _ in range(3):  # Repeat the motion 3 times
        servo_control.move_to(90, velocity=0.5, acceleration=0.1)  # Move to 90 degrees
        time.sleep(1)  # Pause for 1 second
        servo_control.move_to(-90, velocity=0.5, acceleration=0.1)  # Move to -90 degrees
        time.sleep(1)  # Pause for 1 second

    # After the movement is complete, plot the data
    servo_control.plot_data()

except KeyboardInterrupt:
    print("Program stopped")
    servo_control.stop()
