import serial
import time

# Replace 'COM3' with your Arduino's serial port (check in Arduino IDE under Tools > Port)
arduino = serial.Serial('COM5', 9600, timeout=1)
time.sleep(2)  # Wait for the connection to establish

def send_to_arduino(command):
    arduino.write((command + '\n').encode())  # Send command with newline to Arduino

# Function to send signal to Arduino
def control_led(state):
    if state == "on":
        print("sending on to arduino")
        send_to_arduino("on")
    elif state == "off":
        send_to_arduino("off")

# commands = [
#     [50, 100, -25],   # Move motor A 50 steps, motor B 100 steps, motor C -25 steps
#     [30, 50, 0],      # Move motor A 30 steps, motor B 50 steps, motor C 0 steps
#     [0, -75, 20]      # Move motor A 0 steps, motor B -75 steps, motor C 20 steps
# ]

# try:

#     while True:
#         user_input = input("Enter 'y' to turn the LED on, 'n' to turn it off, or anything to quit: ").lower()

#         if user_input == "y":
#             control_led("on")
#             print("LED turned on.")
#         elif user_input == "n":
#             control_led("off")
#             print("LED turned off.")
#         elif user_input == "q" :
#             print("Exiting...")
#             break
#         else:
#             commands = [int(x) for x in input().split()]
#             print(commands)
#             for command in commands:
#                 # Construct command string
#                 command_str = f"A{command[0]},B{command[1]},C{command[2]}"
#                 print(f"Sending command: {command_str}")
#                 send_to_arduino(command_str)  # Send command to Arduino
#                 time.sleep(1)  # Wait for a second before sending the next command


try:
    while True:
        user_input = input("Enter 'y' to turn the LED on, 'n' to turn it off, or anything to quit: ").lower()

        if user_input == "y":
            control_led("on")
            print("LED turned on.")
        elif user_input == "n":
            control_led("off")
            print("LED turned off.")
        elif user_input == "q" :
            print("Exiting...")
            break
        else:
            # Check if the input matches the motor command format (e.g., A50, B100, etc.)
            if len(user_input) > 1 and user_input[0] in ['a', 'b', 'c']:
                motor = user_input[0].upper()  # Motor identifier (A, B, or C)
                try:
                    steps = int(user_input[1:])  # Extract the number of steps
                    command = f"{motor}{steps}"  # Command format: A50, B100, etc.
                    print(f"sendin command : {command}")
                    send_to_arduino(command)  # Send motor command to Arduino
                    print(f"Motor {motor} moved {steps} steps.")
                except ValueError:
                    print("Invalid input. Please enter a valid motor command (e.g., A50, B100, etc.).")
            else:
                print("Invalid input. Please enter 'on', 'off', or a valid motor command.")

except KeyboardInterrupt:
    print("\nProgram interrupted.")

finally:
    # Always close the serial connection when done
    arduino.close()
    print("Serial connection closed.")



# control_led("on")  # Turn on the LED
# time.sleep(5)
# control_led("off")  # Turn off the LED

# # Don't forget to close the connection when done
# arduino.close()
