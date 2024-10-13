import numpy as np
import dash
import dash_core_components as dcc
import dash_html_components as html
from dash.dependencies import Input, Output, State
import plotly.graph_objs as go
import math

# Arm parameters
L1 = 10  # Length of first segment (shoulder to elbow)
L2 = 10  # Length of second segment (elbow to wrist)

stored_angles = []  # List to store angles

# Inverse kinematics function
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
    print(f"theatas are - {np.degrees(theta1):.2f}, {np.degrees(theta2):.2f}, {np.degrees(theta3):.2f}")
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
    print(f"calculated x y and z are {wrist_x, wrist_y, wrist_z}")
    
    return np.array([elbow_x, elbow_y, elbow_z]), np.array([wrist_x, wrist_y, wrist_z])

def angle_to_step(angle1, angle2, angle3, steps_per_rev_1=800, steps_per_rev_2=1600, steps_per_rev_3 = 800):
    steps1 = int((angle1 * steps_per_rev_1) / 360)
    steps2 = int((angle2 * steps_per_rev_2) / 360)
    steps3 = int((angle3 * steps_per_rev_3) / 360)
    print(f"steps1 is {steps1}\nsteps2 is {steps2}\nsteps3 is {steps3}")
    return steps1, steps2, steps3


# Dash app
app = dash.Dash(__name__)

app.layout = html.Div([
    dcc.Graph(id='3d-arm', style={'height': '600px'}),
    html.Div([
        html.Label('X Coordinate', style={'fontWeight': 'bold', 'fontSize': '16px'}),
        dcc.Slider(id='x-slider', min=-20, max=20, step=0.1, value=15, 
                   marks={i: str(i) for i in range(-20, 21, 5)},
                   tooltip={"placement": "bottom", "always_visible": True}, updatemode='drag'),
    ], style={'padding': '10px'}),
    html.Div([
        html.Label('Y Coordinate', style={'fontWeight': 'bold', 'fontSize': '16px'}),
        dcc.Slider(id='y-slider', min=-20, max=20, step=0.1, value=0,
                   marks={i: str(i) for i in range(-20, 21, 5)},
                   tooltip={"placement": "bottom", "always_visible": True}, updatemode='drag'),
    ], style={'padding': '10px'}),
    html.Div([
        html.Label('Z Coordinate', style={'fontWeight': 'bold', 'fontSize': '16px'}),
        dcc.Slider(id='z-slider', min=-20, max=20, step=0.1, value=0,
                   marks={i: str(i) for i in range(-20, 21, 5)},
                   tooltip={"placement": "bottom", "always_visible": True}, updatemode='drag'),
    ], style={'padding': '10px'}),
    html.Button('Store Angles', id='store-btn', n_clicks=0, style={'margin': '10px', 'padding': '10px'}),
    html.Button('Move', id='move-btn', n_clicks=0, style={'margin': '10px', 'padding': '10px'}),
    dcc.Store(id='angles-store', data=stored_angles),
])

@app.callback(
    [Output('3d-arm', 'figure'),
     Output('angles-store', 'data')],
    [Input('x-slider', 'value'),
     Input('y-slider', 'value'),
     Input('z-slider', 'value'),
     Input('store-btn', 'n_clicks')],
    [State('3d-arm', 'figure'), State('angles-store', 'data')]
)
def update_graph(x, y, z, n_clicks, existing_fig, angles_list):
    theta1, theta2, theta3 = inverse_kinematics(x, y, z)
   
    elbow_pos, wrist_pos = forward_kinematics(theta1, theta2, theta3)
    step1, step2, step3 = angle_to_step(theta1, theta2, theta3)

    # Create axis and arm lines
    axes = [
        go.Scatter3d(x=[0, 20], y=[0, 0], z=[0, 0], mode='lines', line=dict(color='black', width=3), name='X-axis'),
        go.Scatter3d(x=[0, 0], y=[0, 20], z=[0, 0], mode='lines', line=dict(color='black', width=3), name='Y-axis'),
        go.Scatter3d(x=[0, 0], y=[0, 0], z=[0, 20], mode='lines', line=dict(color='black', width=3), name='Z-axis'),
    ]
    
    arm_segments = go.Scatter3d(
        x=[0, elbow_pos[0], wrist_pos[0]],
        y=[0, elbow_pos[1], wrist_pos[1]],
        z=[0, elbow_pos[2], wrist_pos[2]],
        mode='lines+markers+text',
        line=dict(color='blue', width=5),
        marker=dict(size=5, color=['red', 'black', 'green']),
        text=[None, f'{np.degrees(theta3):.2f}°', f'{np.degrees(theta2):.2f}°'],
        textposition="top center",
        name='Arm'
    )
    
    # Store angles if 'Store Angles' button is clicked
    if n_clicks > len(angles_list):
        angles_list.append([np.degrees(theta1), np.degrees(theta2), np.degrees(theta3)])

    data = axes + [arm_segments]
    layout = go.Layout(
        scene=dict(
            xaxis=dict(range=[-20, 20]),
            yaxis=dict(range=[-20, 20]),
            zaxis=dict(range=[-20, 20]),
            aspectmode='cube'
        ),
        margin=dict(l=0, r=0, b=0, t=0)
    )

    if existing_fig:
        # Retain the camera (view) settings from the previous figure
        layout.scene.camera = existing_fig['layout']['scene'].get('camera')

    return go.Figure(data=data, layout=layout), angles_list

@app.callback(
    Output('angles-store', 'clear_data'),
    Input('move-btn', 'n_clicks'),
    State('angles-store', 'data')
)
def move(n_clicks, angles_list):
    if n_clicks > 0:
        # Print the angles list and exit the program
        print("Stored Angles:", angles_list)
        exit()
    return dash.no_update

if __name__ == '__main__':
    app.run_server(debug=True)
