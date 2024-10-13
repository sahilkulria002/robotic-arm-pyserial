import numpy as np
import math

# Arm lengths
L1 = 10  # Length of the first arm segment
L2 = 10  # Length of the second arm segment

def inverse_kinematics(x, y, z):
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
    theta2, theta3 = inverse_kinematics2(r,z,L1, L2)
    
    # Calculate theta3 as the angle between the two links
    # theta3 = np.arccos((L1**2 + L2**2 - d**2) / (2 * L1 * L2))    
    return theta1, theta2, theta3

def inverse_kinematics2(x, y, L1, L2):
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
def forward_kinematics(theta1, theta2, theta3):
    # Calculate elbow position
    elbow_x = L1 * np.cos(theta1) * np.cos(theta2)
    elbow_y = L1 * np.sin(theta1) * np.cos(theta2)
    elbow_z = L1 * np.sin(theta2)
    
    # Calculate wrist position
    wrist_x = elbow_x + L2 * np.cos(theta1) * np.cos(theta2 + theta3)
    wrist_y = elbow_y + L2 * np.sin(theta1) * np.cos(theta2 + theta3)
    wrist_z = elbow_z + L2 * np.sin(theta2 + theta3)
    
    return np.array([elbow_x, elbow_y, elbow_z]), np.array([wrist_x, wrist_y, wrist_z])

# Example Usage
x_target = 10
y_target = 10
z_target = 10

# Inverse Kinematics
theta1, theta2, theta3 = inverse_kinematics(x_target, y_target, z_target)

# Forward Kinematics
elbow_pos, wrist_pos = forward_kinematics(theta1, theta2, theta3)

# Print results
print("Original (x, y, z):", (x_target, y_target, z_target))
print(f"theatas are - {np.degrees(theta1):.2f}, {np.degrees(theta2):.2f}, {np.degrees(theta3):.2f}")
print("Calculated Wrist Position:", wrist_pos)
