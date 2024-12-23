import pygame
import math

# Function to calculate the joint positions using angles
def get_joint_positions(theta1, theta2, origin, L1, L2):
    elbow_x = origin[0] + L1 * math.cos(theta1)
    elbow_y = origin[1] + L1 * math.sin(theta1)
    tip_x = elbow_x + L2 * math.cos(theta1 + theta2)
    tip_y = elbow_y + L2 * math.sin(theta1 + theta2)
    return (elbow_x, elbow_y), (tip_x, tip_y)

# Inverse Kinematics to calculate the angles based on the tip's position
def inverse_kinematics(x, y, L1, L2):
    dist = math.sqrt(x**2 + y**2)
    if dist > (L1 + L2):
        return None, None
    cos_angle2 = (x**2 + y**2 - L1**2 - L2**2) / (2 * L1 * L2)
    theta2 = math.acos(cos_angle2)
    k1 = L1 + L2 * cos_angle2
    k2 = L2 * math.sin(theta2)
    theta1 = math.atan2(y, x) - math.atan2(k2, k1)
    return theta1, theta2

# Function to convert angle changes to stepper motor steps
def angle_to_step(angle1, angle2, steps_per_rev_1=2200, steps_per_rev_2=5000):
    steps1 = int((angle1 * steps_per_rev_1) / 360)
    steps2 = int((angle2 * steps_per_rev_2) / 360)
    print(f"steps1 is {steps1}\nsteps2 is {steps2}")
    return steps1, steps2

# The main UI function that returns angles when "Move" is pressed
def run_ui():
    # Arm lengths
    L1 = 180  # Length of the first segment (stick 1)
    L2 = 120  # Length of the second segment (stick 2)

    # Colors
    WHITE = (255, 255, 255)
    BLACK = (0, 0, 0)
    RED = (255, 0, 0)
    GREEN = (0, 255, 0)

    # Initialize pygame
    pygame.init()
    WIDTH, HEIGHT = 800, 600
    screen = pygame.display.set_mode((WIDTH, HEIGHT))
    pygame.display.set_caption('2-DOF Robotic Arm')

    # Origin point (the shoulder of the arm)
    origin = (WIDTH // 2, HEIGHT // 2)

    # Button setup
    BUTTON_WIDTH, BUTTON_HEIGHT = 100, 50
    go_button_color = GREEN
    go_button_rect = pygame.Rect(WIDTH - BUTTON_WIDTH - 10, HEIGHT - BUTTON_HEIGHT - 10, BUTTON_WIDTH, BUTTON_HEIGHT)

    move_button_color = RED
    move_button_rect = pygame.Rect(WIDTH - BUTTON_WIDTH - 10, HEIGHT - (BUTTON_HEIGHT * 2) - 20, BUTTON_WIDTH, BUTTON_HEIGHT)

    running = True
    arm_angles = [0, 0]
    move_arm = False
    final_angles = None
    prev_angle1 = 0
    prev_angle2 = 0
    steps_list = []

    while running:
        screen.fill(WHITE)

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

            # Check if the mouse button is pressed
            if event.type == pygame.MOUSEBUTTONDOWN:
                if event.button == 1:
                    move_arm = True  # Start moving the arm
                    # Get initial mouse position for inverse kinematics
                    mouse_x, mouse_y = pygame.mouse.get_pos()
                    rel_x = mouse_x - origin[0]
                    rel_y = mouse_y - origin[1]
                    theta1, theta2 = inverse_kinematics(rel_x, rel_y, L1, L2)

                    if theta1 is not None and theta2 is not None:
                        arm_angles = [theta1, theta2]
                        final_angles = [theta1, theta2]

            # Check if mouse button is released
            if event.type == pygame.MOUSEBUTTONUP:
                if event.button == 1:
                    move_arm = False  # Stop moving the arm

            # Process button presses
            if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                if go_button_rect.collidepoint(event.pos):
                    if final_angles:
                        # Calculate angle changes
                        final_angle1 = int(math.degrees(final_angles[0]))
                        final_angle2 = int(math.degrees(final_angles[1]))

                        angle1_change = final_angle1 - prev_angle1
                        angle2_change = final_angle2 - prev_angle2

                        # Convert to steps and append to the list
                        steps1, steps2 = angle_to_step(angle1_change, angle2_change)
                        steps_list.append([steps1, steps2])  # Append to the list

                        # Update previous angles
                        prev_angle1 = final_angle1
                        prev_angle2 = final_angle2

                elif move_button_rect.collidepoint(event.pos):
                    pygame.quit()
                    return steps_list  # Return the list of steps when Move button is pressed

        # If the mouse is pressed, update arm angles
        if move_arm:
            mouse_x, mouse_y = pygame.mouse.get_pos()
            rel_x = mouse_x - origin[0]
            rel_y = mouse_y - origin[1]
            theta1, theta2 = inverse_kinematics(rel_x, rel_y, L1, L2)

            if theta1 is not None and theta2 is not None:
                arm_angles = [theta1, theta2]
                final_angles = [theta1, theta2]

        elbow_pos, tip_pos = get_joint_positions(arm_angles[0], arm_angles[1], origin, L1, L2)

        pygame.draw.line(screen, BLACK, origin, elbow_pos, 5)
        pygame.draw.line(screen, BLACK, elbow_pos, tip_pos, 5)
        pygame.draw.circle(screen, RED, origin, 10)
        pygame.draw.circle(screen, RED, elbow_pos, 10)
        pygame.draw.circle(screen, RED, tip_pos, 10)

        # Draw the Go button
        pygame.draw.rect(screen, go_button_color, go_button_rect)
        font = pygame.font.Font(None, 36)
        go_button_text = font.render("Store", True, BLACK)
        screen.blit(go_button_text, (go_button_rect.x + 20, go_button_rect.y + 10))

        # Draw the Move button
        pygame.draw.rect(screen, move_button_color, move_button_rect)
        move_button_text = font.render("Move", True, BLACK)
        screen.blit(move_button_text, (move_button_rect.x + 10, move_button_rect.y + 10))

        # Display angles
        angles_text = font.render(f'Angle 1: {math.degrees(arm_angles[0]):.2f}°  Angle 2: {math.degrees(arm_angles[1]):.2f}°', True, BLACK)
        screen.blit(angles_text, (10, 10))

        pygame.display.flip()

    pygame.quit()

def main():
    while True:
        # Call the UI function which returns steps when "Move" is pressed
        steps_list = run_ui()
        print("Steps list:", steps_list)  # You can use this list as needed

if __name__ == '__main__':
    main()
