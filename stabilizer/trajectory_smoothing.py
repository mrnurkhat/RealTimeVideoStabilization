from plot_trajectory import PlotTrajectory

class TrajectorySmoother:
    def __init__(self, Q=5e-5, R=3e-2, enable_plot=False):
        self.x_raw_cumulative = 0
        self.y_raw_cumulative = 0
        self.r_raw_cumulative = 0

        self.kalman_x = Kalman1D(Q, R)
        self.kalman_y = Kalman1D(Q, R)
        self.kalman_r = Kalman1D(Q, R)

        self.trajectory_plotter = PlotTrajectory(enable_plot)

    def smooth(self, dx_raw, dy_raw, dr_raw):
        self.x_raw_cumulative += dx_raw
        self.y_raw_cumulative += dy_raw
        self.r_raw_cumulative += dr_raw

        x_smooth = self.kalman_x.update(self.x_raw_cumulative)
        y_smooth = self.kalman_y.update(self.y_raw_cumulative)
        r_smooth = self.kalman_r.update(self.r_raw_cumulative)

        self.trajectory_plotter.collect(
            self.x_raw_cumulative,
            self.y_raw_cumulative,
            self.r_raw_cumulative,
            x_smooth,
            y_smooth,
            r_smooth
        )

        return x_smooth, y_smooth, r_smooth

    def display_trajectory(self):
        self.trajectory_plotter.display()
    

class Kalman1D:
    def __init__(self, Q=5e-5, R=3e-2, x0=0):
        self.Q = Q
        self.R = R
        self.x = x0
        self.P = 1.0

    def update(self, measurement):
        xPred = self.x
        PPred = self.P + self.Q

        K = PPred / (PPred + self.R)
        self.x = xPred + K * (measurement - xPred)
        self.P = (1 - K) * PPred

        return self.x