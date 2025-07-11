import cv2 as cv

from stabilizer import Stabilizer
from source import FrameSource
from visualizer import TrajectoryPlotter
from logger import Logger
import utils


def main():
    # Load and validate the configuration from a JSON file
    config = utils.load_and_validate_config("config.json")

    # Initialize the video/frame source (camera or video file)
    source = FrameSource(config) 

    # Initialize the trajectory visualizer and logger
    plotter = TrajectoryPlotter(config)
    logger = Logger(config)
    
    # Initialize the stabilizer with the first frame
    first_frame = source.read()
    stabilizer = Stabilizer(config, first_frame, logger)

    # Prepare the video writer if needed
    h, w = first_frame.shape[:2]
    writer = utils.init_video_writer(config, (w, h))

    # Main loop for reading, stabilizing, and writing frames
    while True:
        # Read the next frame
        curr = source.read()
        if curr is None:
            break
        
        # Stabilize the current frame
        result = stabilizer.stabilize(curr)

        # Collect trajectory data for plotting if nedded
        plotter.collect(stabilizer.export_trajectory_data())

        # Optionally crop the stabilized frame
        result = utils.crop_stabilized_frame(config, result)

        # Optionally display the original and stabilized frame side by side
        is_display_on, result = utils.show_result(config, result, curr)

        # Write the stabilized frame to the output video if enabled
        if writer is not None:
            writer.write(result)

        # Exit the loop if the user pressed the ESC key
        if utils.check_esc(is_display_on):
            break
    
    # Release the video source
    source.release()

    # Close display windows if needed
    if is_display_on:
        cv.destroyAllWindows()

    # Release the video writer if it was initialized
    if writer is not None:
        writer.release()

    # Save log data to file
    logger.save_log()

    # Show the estimated trajectory plot after processing
    plotter.display()

if __name__ == "__main__":
    main()