import time
import psutil

class Logger:
    def __init__(self, config):
        # Logging flags based on configuration
        self.log_msg = config["log_message"]  # Whether to log standard messages
        self.log_measure = config["measure_performance"]  # Whether to log performance metrics
        
        # Optional log file output
        self.save_log_to = config["save_log_to"]
        self.log_history = [] if self.save_log_to else None

        # Frame tracking
        self.frame_counter = 1
        self.drop_count = 0
        self.success_count = 0
        self.start_time = time.time()

        # Setup process monitoring (for CPU and memory usage)
        self.process = psutil.Process()
        self.process.cpu_percent(interval=None)

    def log(self, msg, type = "INFO"):
        """
        Log a message of the given type. Types can be 'INFO' or 'MEASURMENT'.
        Only logs if enabled via config.
        """
        if not self.log_measure and type == "MEASURMENT":
            return
        if not self.log_msg and type != "MEASURMENT":
            return

        full = f"[{type}] [Frame {self.frame_counter}] {msg}"
        print(full)

        # Save to history if logging to file is enabled
        if self.log_history is not None:
            self.log_history.append(full)

    def update_status(self, success: bool):
        """
        Call this after processing each frame to update success/failure counters.
        Logs performance every 100 frames if enabled.
        """
        self.frame_counter += 1
        if success:
            self.success_count += 1
        else:
            self.drop_count += 1

        # Every 100 frames, report performance metrics
        if self.frame_counter % 100 == 0 and self.log_measure:
            elapsed = time.time() - self.start_time
            fps = 100 / elapsed if elapsed > 0 else 0
            cpu = self.process.cpu_percent() # Instantaneous CPU usage
            mem_mb = self.process.memory_info().rss / 1024 / 1024 # Memory in MB
            drop_rate = 100 * self.drop_count / (self.success_count + self.drop_count) if (self.success_count + self.drop_count) > 0 else 0

            self.log(
                f"Avg FPS: {fps:.1f} | CPU: {cpu:.1f}% | Mem: {mem_mb:.1f} MB | Dropped: {drop_rate:.1f}%",
                "MEASURMENT"
            )
            self.start_time = time.time()
            self.drop_count = 0
            self.success_count = 0

    def save_log(self):
        """
        Save the log history to a file if logging was enabled and a path is set.
        """
        if not self.log_history:
            return
        try:
            with open(self.save_log_to, "w") as f:
                f.write("\n".join(self.log_history))
            print(f"[INFO] Log saved to {self.save_log_to}")
        except Exception as e:
            print(f"[ERROR] Failed to save log: {e}")