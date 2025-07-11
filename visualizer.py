import matplotlib.pyplot as plt
import numpy as np


class TrajectoryPlotter:
    def __init__(self, config):
        # Check if trajectory plotting is enabled in the config
        self.enabled = config["plot_trajectory"]
        if not self.enabled:
            return 
        
        # Initialize containers for raw and smoothed trajectory data (translation (x, y) + angle (r))
        self.raw = {"x": [], "y": [], "r": []}
        self.smooth = {"x": [], "y": [], "r": []}

    def collect(self, trajectory):
        # Skip if plotting is disabled
        if not self.enabled:
            return
        
        # Append new data for raw and smoothed trajectories
        self.raw["x"].append(trajectory[0])
        self.raw["y"].append(trajectory[1])
        self.raw["r"].append(trajectory[2])
        self.smooth["x"].append(trajectory[3])
        self.smooth["y"].append(trajectory[4])
        self.smooth["r"].append(trajectory[5])

    def display(self):
        # Skip if plotting is disabled
        if not self.enabled:
            return
        
        # Keys and labels for plotting
        keys = ["x", "y", "r"]
        labels = ["X", "Y", "Angle (°)"]

        # Create subplots for each trajectory component
        fig, axs = plt.subplots(len(keys), 1, figsize=(10, 8), sharex=True)
        fig.suptitle("Camera Trajectories (Raw vs Smoothed)", fontsize=12)

        # Plot raw vs smoothed trajectories
        for i, key in enumerate(keys):
            raw_data = self.raw[key]
            smooth_data = self.smooth[key]

            # Convert angles from radians to degrees
            if key == "r":
                raw_data = np.degrees(raw_data)
                smooth_data = np.degrees(smooth_data)
                
            axs[i].plot(raw_data, label="Raw")
            axs[i].plot(smooth_data, label="Smooth")
            axs[i].legend()
            axs[i].set_ylabel(labels[i])
            axs[i].grid(True)
        axs[2].set_xlabel("Frames")

        plt.tight_layout(rect=[0, 0, 1, 0.95])
        plt.show()