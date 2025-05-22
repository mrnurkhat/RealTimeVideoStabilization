from plot_trajectory import PlotTrajectory

class TrajectorySmoother:
    def __init__(self, Q=5e-5, R=3e-2):
        self.x_raw_sum = 0
        self.y_raw_sum = 0
        self.r_raw_sum = 0

        self.kalman_x = Kalman1D(Q, R)
        self.kalman_y = Kalman1D(Q, R)
        self.kalman_r = Kalman1D(Q, R)
    
    def cumulate(self, dx_raw, dy_raw, dr_raw):
        self.x_raw_sum += dx_raw
        self.y_raw_sum += dy_raw
        self.r_raw_sum += dr_raw

        return self.x_raw_sum, self.y_raw_sum, self.r_raw_sum

    def smooth(self):
        x_smooth_sum = self.kalman_x.update(self.x_raw_sum)
        y_smooth_sum = self.kalman_y.update(self.y_raw_sum)
        r_smooth_sum = self.kalman_r.update(self.r_raw_sum)

        return x_smooth_sum, y_smooth_sum, r_smooth_sum
    

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