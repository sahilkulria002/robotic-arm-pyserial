import numpy as np
import dash
import dash_core_components as dcc
import dash_html_components as html
from dash.dependencies import Input, Output
import plotly.graph_objs as go

# Arm parameters (Lengths of each section)
L1 = 10  # Length of first segment (shoulder to elbow)
L2 = 10  # Length of second segment (elbow to wrist)

# Inverse kinematics function to calculate the angles
def inverse_kinematics(x, y, z):
    r = np.sqrt(x**2 + y**2)
    d = np.sqrt(r**2 + z**2)
    
    # Check if the point is reachable
    if d > (L1 + L2):
        # If out of reach, scale down to maximum reach
        scale = (L1 + L2) / d
        x *= scale
        y *= scale
        z *= scale
        d = L1 + L2
    
    # Calculate inverse kinematics for the two-segment arm
    theta1 = np.arctan2(y, x)  # Base rotation (around Z-axis)
    
    # Using cosine law to calculate the angle at the elbow
    cos_angle = (L1**2 + L2**2 - d**2) / (2 * L1 * L2)
    theta2 = np.arccos(np.clip(cos_angle, -1, 1))
    
    # Calculate the shoulder angle using cosine law
    alpha = np.arctan2(z, r)
    cos_angle_shoulder = (L1**2 + d**2 - L2**2) / (2 * L1 * d)
    shoulder_angle = np.arccos(np.clip(cos_angle_shoulder, -1, 1))
    
    theta3 = alpha + shoulder_angle
    
    return theta1, theta2, theta3

# Forward kinematics function to calculate positions based on angles
def forward_kinematics(theta1, theta2, theta3):
    # Calculate the position of the elbow
    elbow_x = L1 * np.cos(theta1) * np.cos(theta3)
    elbow_y = L1 * np.sin(theta1) * np.cos(theta3)
    elbow_z = L1 * np.sin(theta3)
    
    # Calculate the position of the wrist
    wrist_x = elbow_x + L2 * np.cos(theta1) * np.cos(theta3 - theta2)
    wrist_y = elbow_y + L2 * np.sin(theta1) * np.cos(theta3 - theta2)
    wrist_z = elbow_z + L2 * np.sin(theta3 - theta2)
    
    return np.array([elbow_x, elbow_y, elbow_z]), np.array([wrist_x, wrist_y, wrist_z])

# Initial wrist position (start at the maximum reach)
initial_wrist_position = np.array([L1 + L2, 0, 0])

# Dash app
app = dash.Dash(__name__)

app.layout = html.Div([
    dcc.Graph(id='3d-arm'),
    html.Div([
        html.Label('X Coordinate'),
        dcc.Slider(id='x-slider', min=-20, max=20, step=0.1, value=initial_wrist_position[0]),
    ], style={'padding': '10px'}),
    html.Div([
        html.Label('Y Coordinate'),
        dcc.Slider(id='y-slider', min=-20, max=20, step=0.1, value=initial_wrist_position[1]),
    ], style={'padding': '10px'}),
    html.Div([
        html.Label('Z Coordinate'),
        dcc.Slider(id='z-slider', min=-20, max=20, step=0.1, value=initial_wrist_position[2]),
    ], style={'padding': '10px'}),
])

# Update the 3D plot based on slider inputs
@app.callback(
    Output('3d-arm', 'figure'),
    [Input('x-slider', 'value'),
     Input('y-slider', 'value'),
     Input('z-slider', 'value')]
)
def update_graph(x, y, z):
    # Calculate the angles using inverse kinematics
    theta1, theta2, theta3 = inverse_kinematics(x, y, z)
    
    # Calculate the positions of the elbow and wrist
    elbow_pos, wrist_pos = forward_kinematics(theta1, theta2, theta3)
    
    # Create axis lines
    axes = [
        go.Scatter3d(x=[0, 20], y=[0, 0], z=[0, 0], mode='lines', line=dict(color='black', width=3), name='X-axis'),
        go.Scatter3d(x=[0, 0], y=[0, 20], z=[0, 0], mode='lines', line=dict(color='black', width=3), name='Y-axis'),
        go.Scatter3d(x=[0, 0], y=[0, 0], z=[0, 20], mode='lines', line=dict(color='black', width=3), name='Z-axis'),
    ]
    
    # Create the arm segments
    arm_segments = go.Scatter3d(
        x=[0, elbow_pos[0], wrist_pos[0]],
        y=[0, elbow_pos[1], wrist_pos[1]],
        z=[0, elbow_pos[2], wrist_pos[2]],
        mode='lines+markers',
        line=dict(color='blue', width=5),
        marker=dict(size=5, color=['red', 'black', 'green']),
        name='Arm'
    )
    
    # Combine all elements into the data list
    data = axes + [arm_segments]
    
    # Set the layout for the 3D plot
    layout = go.Layout(
        scene=dict(
            xaxis=dict(range=[-20, 20]),
            yaxis=dict(range=[-20, 20]),
            zaxis=dict(range=[-20, 20]),
            aspectmode='cube'
        ),
        margin=dict(l=0, r=0, b=0, t=0)
    )
    
    return go.Figure(data=data, layout=layout)

if __name__ == '__main__':
    app.run_server(debug=True)
