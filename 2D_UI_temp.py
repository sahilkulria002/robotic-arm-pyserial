import pygame
import math
import sys

# Define constants
WIDTH, HEIGHT = 800, 600
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
ARM_COLOR = (0, 128, 255)
BUTTON_COLOR = (0, 255, 0)
EXIT_BUTTON_COLOR = (255, 0, 0)

# Arm parameters
arm_length1 = 150
arm_length2 = 100
origin = (WIDTH // 2, HEIGHT // 2)

# Initialize Pygame
pygame.init()

# Function to draw the arm based on angles
def draw_arm(screen, angle1, angle2):
    # First joint
    joint1_x = origin[0] + arm_length1 * math.cos(angle1)
    joint1_y = origin[1] - arm_length1 * math.sin(angle1)
    
    # Second joint (end of the arm)
    joint2_x = joint1_x + arm_length2 * math.cos(angle1 + angle2)
    joint2_y = joint1_y - arm_length2 * math.sin(angle1 + angle2)

    # Draw the arm
    pygame.draw.line(screen, ARM_COLOR, origin, (joint1_x, joint1_y), 5)
    pygame.draw.line(screen, ARM_COLOR, (joint1_x, joint1_y), (joint2_x, joint2_y), 5)
    
    return joint2_x, joint2_y

# Function to display buttons and handle UI
def run_ui():
    screen = pygame.display.set_mode((WIDTH, HEIGHT))
    pygame.display.set_caption("2D Robotic Arm Simulation")
    font = pygame.font.Font(None, 36)

    angle1, angle2 = math.radians(45), math.radians(45)
    prev_angle1, prev_angle2 = 0, 0
    final_angles = [angle1, angle2]

    # Button for "Go"
    go_button = pygame.Rect(WIDTH - 150, HEIGHT - 100, 100, 50)
    # Button for "Exit"
    exit_button = pygame.Rect(50, HEIGHT - 100, 100, 50)

    running = True
    while running:
        screen.fill(WHITE)

        # Draw arm
        draw_arm(screen, final_angles[0], final_angles[1])

        # Draw buttons
        pygame.draw.rect(screen, BUTTON_COLOR, go_button)
        pygame.draw.rect(screen, EXIT_BUTTON_COLOR, exit_button)
        screen.blit(font.render("Go", True, BLACK), (WIDTH - 130, HEIGHT - 90))
        screen.blit(font.render("Exit", True, BLACK), (70, HEIGHT - 90))

        # Event handling
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
                return None, None
            elif event.type == pygame.MOUSEBUTTONDOWN:
                if go_button.collidepoint(event.pos):
                    final_angle1 = math.degrees(final_angles[0])
                    final_angle2 = math.degrees(final_angles[1])
                    angle1_change = final_angle1 - prev_angle1
                    angle2_change = final_angle2 - prev_angle2
                    steps1, steps2 = angle_to_step(angle1_change, angle2_change)
                    prev_angle1, prev_angle2 = final_angle1, final_angle2
                    print(f"Angles: {final_angle1}, {final_angle2}")
                    return steps1, steps2
                elif exit_button.collidepoint(event.pos):
                    running = False
                    return None, None

        # Update the display
        pygame.display.flip()

    pygame.quit()

def angle_to_step(angle1, angle2, steps_per_rev_1=400, steps_per_rev_2=1600):
    steps1 = int((angle1 * steps_per_rev_1) / 360)
    steps2 = int((angle2 * steps_per_rev_2) / 360)
    print(f"Steps1: {steps1}, Steps2: {steps2}")
    return steps1, steps2













