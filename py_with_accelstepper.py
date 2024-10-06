import serial
import time
import keyboard  # Make sure to install this library
import two_D_UI

# This connects to the pyserial communication in Arduino
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

def send_commands_to_arduino(commands):
    command_str = ";".join([f"A{cmd[0]},B{cmd[1]},C{cmd[2]}" for cmd in commands])
    print(command_str)
    arduino.write((command_str + '\n').encode())  # Send command to Arduino
    time.sleep(0.1)  # Optional delay after sending commands

# Initialize commands
commands = []

# Function to handle key presses
def handle_keypress(event):
    global commands  # Use the global commands variable
    if event.name == 'up':
        commands = [[10, 0, 0]]  # Set command for up arrow
        print("--- x moving forward")
        send_commands_to_arduino(commands)  # Call function to send command to Arduino
    elif event.name == 'down':
        commands = [[-10, 0, 0]]  # Set command for down arrow
        print("--- x moving backward")
        send_commands_to_arduino(commands)  # Call function to send command to Arduino
    elif event.name == 'left':
        commands = [[0, 10, 0]]  # Set command for left arrow
        print("---  y moving forward")
        send_commands_to_arduino(commands)  # Call function to send command to Arduino
    elif event.name == 'right':
        commands = [[0, -10, 0]]  # Set command for right arrow
        print("---  y moving backward")
        send_commands_to_arduino(commands)  # Call function to send command to Arduino
    elif event.name == 'comma':  # Represents the '<' key
        commands = [[0, 0, 10]]  # Set command for '<' key
        print("---  z moving forward")
        send_commands_to_arduino(commands)  # Call function to send command to Arduino
    elif event.name == 'period':  # Represents the '>' key
        commands = [[0, 0, -10]]  # Set command for '>' key
        print("---  z moving backward")
        send_commands_to_arduino(commands)  # Call function to send command to A,,,,,,...........rduino

# Listen for key presses
keyboard.on_press(handle_keypress)
keyboard.add_hotkey('<', lambda: [print("z moving forward"), send_commands_to_arduino([[0, 0, 10]])])
keyboard.add_hotkey('>', lambda: [print("z moving backward"), send_commands_to_arduino([[0, 0, -10]])])


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
            
            while user_input != "q" :
                commands = []
                step_list = two_D_UI.run_ui()
                for steps in step_list :
                    commands.append([-steps[1], 0, steps[0]])
                send_commands_to_arduino(commands)
                user_input = input("give e to stop or 3 ints, one for each motor : ")

except KeyboardInterrupt:
    print("\nProgram interrupted.")

finally:
    # Always close the serial connection when done
    arduino.close()
    print("Serial connection closed.")