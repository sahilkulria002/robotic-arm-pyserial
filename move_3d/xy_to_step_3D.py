import numpy as np
import math

# Arm lengths
# L1 = 10  # Length of the first arm segment
# L2 = 10  # Length of the second arm segment

def angle_to_step(angle1, angle2, angle3, steps_per_rev_1=2500, steps_per_rev_2=2500, steps_per_rev_3 = 2500):
    angle1_deg = math.degrees(angle1)
    angle2_deg = math.degrees(angle2)
    angle3_deg = math.degrees(angle3)
    
    # Convert degrees to steps
    steps1 = int((angle1_deg * steps_per_rev_1) / 360)
    steps2 = int((angle2_deg * steps_per_rev_2) / 360)
    steps3 = int((angle3_deg * steps_per_rev_3) / 360)
    
    print(f"steps1 is {steps1}\nsteps2 is {steps2}\nsteps3 is {steps3}")
    return steps1, steps2, steps3

def inverse_kinematics(x, y, z,L1=10,L2=10):
    r = np.sqrt(x**2 + y**2)  # Projection in the xy-plane
    d = np.sqrt(r**2 + z**2)   # Distance in 3D space
    
    # Check for reachability
    if d > (L1 + L2):
        scale = (L1 + L2) / d
        x *= scale
        y *= scale
        z *= scale
        d = L1 + L2
    
    # Calculate theta1
    theta1 = np.arctan2(y, x)
    theta2, theta3 = inverse_kinematics2D(r,z,L1, L2)

    # theta1 : 
    # theta2 : 
    # theta3 :
    
    # Calculate theta3 as the angle between the two links
    # theta3 = np.arccos((L1**2 + L2**2 - d**2) / (2 * L1 * L2))    
    return theta1, theta2, theta3

def inverse_kinematics2D(x, y, L1, L2):
    dist = math.sqrt(x**2 + y**2)
    if dist > (L1 + L2):
        return None, None
    cos_angle2 = (x**2 + y**2 - L1**2 - L2**2) / (2 * L1 * L2)
    theta2 = math.acos(cos_angle2)
    k1 = L1 + L2 * cos_angle2
    k2 = L2 * math.sin(theta2)
    theta1 = math.atan2(y, x) - math.atan2(k2, k1)
    return theta1, theta2

# Forward kinematics function
def forward_kinematics(theta1, theta2, theta3, L1=10, L2=10):
    # Calculate elbow position
    elbow_x = L1 * np.cos(theta1) * np.cos(theta2)
    elbow_y = L1 * np.sin(theta1) * np.cos(theta2)
    elbow_z = L1 * np.sin(theta2)
    
    # Calculate wrist position
    wrist_x = elbow_x + L2 * np.cos(theta1) * np.cos(theta2 + theta3)
    wrist_y = elbow_y + L2 * np.sin(theta1) * np.cos(theta2 + theta3)
    wrist_z = elbow_z + L2 * np.sin(theta2 + theta3)
    
    return np.array([elbow_x, elbow_y, elbow_z]), np.array([wrist_x, wrist_y, wrist_z])

# def xyz_to_steps(curve, L1=15, L2=15) :
#     """
#     for given x,y,z it will return step1, step2, step3 ie shoulder1, shoulder2, elbow

#     """
#     commands = []
#     for x,y,z in curve :
#         angle1, angle2, angl3 = inverse_kinematics(x,y,z) 
#         step1, step2, step3 = angle_to_step(angle1, angle2, angl3)
#         commands.append[step1, step2, step3]
#     return commands

def xyz_to_steps(curve, L1=21, L2=15):
    """
    Calculates the steps for each joint to move the robotic arm to each point in the curve,
    considering the current position.
    """
    commands = []
    
    # Initial angles (assuming starting from 0)
    current_theta1, current_theta2, current_theta3 = 0, 0, 0
    
    for x, y, z in curve:
        theta1, theta2, theta3 = inverse_kinematics(x, y, z, L1, L2)
        
        # Calculate angle differences (relative movement)
        delta_theta1 = theta1 - current_theta1
        delta_theta2 = theta2 - current_theta2
        delta_theta3 = theta3 - current_theta3
        
        # Convert the angle differences to steps
        step1, step2, step3 = angle_to_step(delta_theta1, delta_theta2, delta_theta3)
        
        # Append the step commands
        commands.append([-step3, step1, step2])
        # commands.append([-steps[2], steps[0], steps[1]])
        
        # Update current angles to the new ones
        current_theta1, current_theta2, current_theta3 = theta1, theta2, theta3
    
    return commands


# Example Usage
def main():
    curve = []
    while True :
        st = input("give position as x y z : or q to exit")
        while st != "q" :
            x_target, y_target, z_target = map(int, st.split())
            curve.append([x_target, y_target, z_target])
            st = input("give position as x y z : or q to exit")

        cmds = xyz_to_steps(curve)
        print(cmds)


if __name__ == '__main__':
    main()
