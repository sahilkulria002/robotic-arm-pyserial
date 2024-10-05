import sys
from PyQt5.QtWidgets import QApplication, QMainWindow, QPushButton, QVBoxLayout, QWidget
import pyvista as pv
from pyvistaqt import QtInteractor
import numpy as np


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()

        self.setWindowTitle("3D Robotic Arm UI")

        # Layout for the buttons
        self.store_button = QPushButton("Store")
        self.move_button = QPushButton("Move")

        self.store_button.clicked.connect(self.store_clicked)
        self.move_button.clicked.connect(self.move_clicked)

        # Create a layout and add the buttons
        button_layout = QVBoxLayout()
        button_layout.addWidget(self.store_button)
        button_layout.addWidget(self.move_button)

        # Set up the main layout
        self.main_layout = QVBoxLayout()

        # Add button layout to the main layout
        self.main_layout.addLayout(button_layout)

        # Add the 3D rendering area
        self.pv_widget = QtInteractor(self)  # Create PyVista interactor for 3D scene
        self.main_layout.addWidget(self.pv_widget.interactor)

        # Set the central widget for the main window
        container = QWidget()
        container.setLayout(self.main_layout)
        self.setCentralWidget(container)

        # Initialize the 3D scene
        self.create_3d_scene()

    def create_3d_scene(self):
        """Set up the 3D scene with a robotic arm and coordinate axes"""
        plotter = self.pv_widget  # Get the plotter object for rendering

        # Fix the view so it doesn't change while dragging the arm
        plotter.camera_position = 'xy'  # Set to xy plane view

        # Add x, y, z axes to the scene
        plotter.add_axes()

        # Arm link lengths
        self.L1 = 2.0  # Length of the first link
        self.L2 = 2.0  # Length of the second link

        # Add first link (vertical cylinder)
        self.cylinder1 = pv.Cylinder(radius=0.05, height=self.L1, center=(0, self.L1 / 2, 0), direction=(0, 1, 0))
        self.actor1 = plotter.add_mesh(self.cylinder1, color="red", show_edges=True)

        # Add second link (horizontal cylinder attached to the first link)
        self.cylinder2 = pv.Cylinder(radius=0.05, height=self.L2, center=(self.L2 / 2, self.L1, 0), direction=(1, 0, 0))
        self.actor2 = plotter.add_mesh(self.cylinder2, color="blue", show_edges=True)

        # Add indicator spheres at the joints and tip
        self.joint1_sphere = plotter.add_mesh(pv.Sphere(radius=0.1, center=(0, 0, 0)), color="green")  # Base joint
        self.joint2_sphere = plotter.add_mesh(pv.Sphere(radius=0.1, center=(0, self.L1, 0)), color="green")  # Second joint
        self.tip_sphere = plotter.add_mesh(pv.Sphere(radius=0.1, center=(self.L2, self.L1, 0)), color="green")  # Tip of the arm

        # Enable point picking for the tip to drag
        plotter.enable_point_picking(callback=self.drag_callback, left_clicking=True, show_message=False)

        # Render the scene
        plotter.show()

    def drag_callback(self, point):
        """Callback function for dragging the tip of the arm"""
        print(f"Dragged to: {point}")

        # Calculate the new joint angles based on the dragged position
        angles = self.inverse_kinematics(point[:2])  # Ignore z-axis since we're in 2D
        if angles:
            self.update_arm(angles)

    def inverse_kinematics(self, point):
        """Calculate the joint angles based on the end-effector position (2D IK for 2-link arm)"""
        x, y = point  # We only care about x, y in this 2D setup

        L1, L2 = self.L1, self.L2  # Link lengths

        # Distance from the origin to the point
        distance = np.sqrt(x**2 + y**2)

        # Check if the point is reachable
        if distance > L1 + L2 or distance < abs(L1 - L2):
            print("Point is out of reach")
            return None

        # Inverse kinematics calculations
        cos_theta2 = (x**2 + y**2 - L1**2 - L2**2) / (2 * L1 * L2)
        sin_theta2 = np.sqrt(1 - cos_theta2**2)
        theta2 = np.arctan2(sin_theta2, cos_theta2)

        k1 = L1 + L2 * cos_theta2
        k2 = L2 * sin_theta2
        theta1 = np.arctan2(y, x) - np.arctan2(k2, k1)

        return theta1, theta2

    def update_arm(self, angles):
        """Update the arm's position based on the calculated joint angles"""
        theta1, theta2 = angles

        # Calculate the new positions of the joints
        x1 = self.L1 * np.cos(theta1)
        y1 = self.L1 * np.sin(theta1)

        x2 = x1 + self.L2 * np.cos(theta1 + theta2)
        y2 = y1 + self.L2 * np.sin(theta1 + theta2)

        # Update the positions of the links and spheres
        self.cylinder1.transform.translate((0, y1 / 2, 0), inplace=True)
        self.cylinder2.transform.translate((x1 + x2) / 2, y1, 0, inplace=True)

        # Update the spheres (joints)
        self.joint2_sphere.SetPosition(x1, y1, 0)
        self.tip_sphere.SetPosition(x2, y2, 0)

        # Redraw the scene
        self.pv_widget.update()

    def store_clicked(self):
        print("Store button clicked")

    def move_clicked(self):
        print("Move button clicked")


if __name__ == '__main__':
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()  # Show the main window
    sys.exit(app.exec_())
