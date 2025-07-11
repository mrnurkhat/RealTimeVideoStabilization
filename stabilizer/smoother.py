import numpy as np
from filterpy.kalman import KalmanFilter

class MotionFilter:
    def __init__(self, Q, R, max_x, max_y, max_r):
        """
        Initializes Kalman filters for each motion component (x, y, rotation).

        Args:
            Q (float): Process noise covariance.
            R (float): Measurement noise covariance.
        """
        # Max pixel shift
        self.max_x = max_x
        self.max_y = max_y

        # Max rotation in radians
        self.max_r = max_r
       
        # Cumulative raw and smoothed motion
        self.x_raw_sum = 0
        self.y_raw_sum = 0
        self.r_raw_sum = 0

        self.x_smooth_sum = 0
        self.y_smooth_sum = 0
        self.r_smooth_sum = 0

        # Independent 1D Kalman filters
        self.kalman_x = Kalman1D(Q, R)
        self.kalman_y = Kalman1D(Q, R)
        self.kalman_r = Kalman1D(Q, R)
    
    def cumulate(self, raw_motion):
        """Accumulates raw motion over time."""
        self.x_raw_sum += raw_motion[0]
        self.y_raw_sum += raw_motion[1]
        self.r_raw_sum += raw_motion[2]

    def smooth(self):
        """Applies Kalman filtering to each motion component."""
        self.x_smooth_sum = self.kalman_x.update(self.x_raw_sum)
        self.y_smooth_sum = self.kalman_y.update(self.y_raw_sum)
        self.r_smooth_sum = self.kalman_r.update(self.r_raw_sum)
    
    def compute_correction(self):
        """
        Calculates the difference between smoothed and raw motion.
        Applies clamping to prevent overcorrection.
        """
        dx_corr = (self.x_smooth_sum - self.x_raw_sum) 
        dy_corr = (self.y_smooth_sum - self.y_raw_sum)
        dr_corr = (self.r_smooth_sum - self.r_raw_sum)

        dx_corr = np.clip(dx_corr, -self.max_x, self.max_x)
        dy_corr = np.clip(dy_corr, -self.max_y, self.max_y)
        dr_corr = np.clip(dr_corr, -self.max_r, self.max_r)

        return dx_corr, dy_corr, dr_corr
    
    def get_raw_and_smoothed_trajectory(self):
        return self.x_raw_sum, self.y_raw_sum, self.r_raw_sum, self.x_smooth_sum, self.y_smooth_sum, self.r_smooth_sum
   
class Kalman1D:
    def __init__(self, Q=1e-4, R=1e-1, dt=1.0):
        self.dt = dt
        self.kf = KalmanFilter(dim_x=2, dim_z=1)
        self.kf.x = np.zeros((2, 1))

        self.kf.F = np.array([[1, dt], [0, 1]])
        self.kf.H = np.array([[1, 0]])

        self.kf.P *= 1.0
        self.kf.R *= R
        self.kf.Q = Q * np.array([[dt**4/4, dt**3/2], [dt**3/2, dt**2]])

    def update(self, measurement):
        self.kf.predict()
        self.kf.update(np.array([[measurement]]))
        return self.kf.x[0, 0]