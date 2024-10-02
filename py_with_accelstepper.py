import serial
import time
import two_D_UI


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


def send_commands_to_arduino(commands):
    command_str = ";".join([f"A{cmd[0]},B{cmd[1]},C{cmd[2]}" for cmd in commands])
    print(command_str)
    arduino.write((command_str + '\n').encode())  # Send command to Arduino
    time.sleep(0.1)  # Optional delay after sending commands

# commands = [
#     [50, 100, -25],   # Move motor A 50 steps, motor B 100 steps, motor C -25 steps
    # [30, 50, 0],      # Move motor A 30 steps, motor B 50 steps, motor C 0 steps
    # [0, -75, 20]      # Move motor A 0 steps, motor B -75 steps, motor C 20 steps
# ]

# 10 20 0
# -10 -20 0

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
            
            while True :
                user_input = input("give e to stop or 3 ints, one for each motor : ")
                if user_input == "e" :
                    break
                else :
                    commands = []
                    step_list = two_D_UI.run_ui()
                    for steps in step_list :
                        commands.append([-steps[1], 0, steps[0]])
                    send_commands_to_arduino(commands)
                # user_input = input("give e to stop or 3 ints, one for each motor : ")
                # if user_input == "e" :
                #     print(commands)
                #     send_commands_to_arduino(commands)
                #     break
                # else : 
                #     steps = list(map(int, user_input.split()))
                    
                #     if len(steps) != 3:
                #         print("Please enter exactly three integers.")
                #         continue
                    
                #     # Append the steps to the commands list
                #     commands.append(steps)
                #     print(f"Command added: {steps}")


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
