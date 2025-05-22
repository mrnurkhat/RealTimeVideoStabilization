import matplotlib.pyplot as plt
import numpy as np


class PlotTrajectory:
    def __init__(self, enabled: bool):
        self.enabled = enabled
        if self.enabled:
            self.raw = {"x": [], "y": [], "a": []}
            self.smooth = {"x": [], "y": [], "a": []}

    def collect(self, x_raw, y_raw, a_raw, x_smooth, y_smooth, a_smooth):
        if not self.enabled:
            return
        self.raw["x"].append(x_raw)
        self.raw["y"].append(y_raw)
        self.raw["a"].append(a_raw)
        self.smooth["x"].append(x_smooth)
        self.smooth["y"].append(y_smooth)
        self.smooth["a"].append(a_smooth)

    def display(self):
        if not self.enabled:
            return
        keys = ["x", "y", "a"]
        labels = ["X", "Y", "Angle (°)"]
        fig, axs = plt.subplots(len(keys), 1, figsize=(10, 8), sharex=True)
        fig.suptitle("Camera Trajectories (Raw vs Smoothed)", fontsize=12)

        for i, key in enumerate(keys):
            raw_data = self.raw[key]
            smooth_data = self.smooth[key]
            if key == "a":
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

    def _plot_trajectory(self, raw, smooth, label, ylabel):
        if not self.enabled:
            return
        plt.plot(raw, label="Raw")
        plt.plot(smooth, label="Smooth")
        plt.legend()
        plt.ylabel(ylabel)
        plt.xlabel("Frames")
        plt.grid(True)
        plt.title(f"{label} trajectory")
        plt.show()

    def display_x(self):
        self._plot_trajectory(self.raw["x"], self.smooth["x"], "Horizontal", "X")

    def display_y(self):
        self._plot_trajectory(self.raw["y"], self.smooth["y"], "Vertical", "Y")

    def display_a(self):
        self._plot_trajectory(
            np.degrees(self.raw["a"]),
            np.degrees(self.smooth["a"]),
            "Rotation",
            "Angle (°)",
        )
