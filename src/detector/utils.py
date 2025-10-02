def calculate_frame_difference(frame1, frame2):
    # Calculate the absolute difference between two frames
    return cv2.absdiff(frame1, frame2)

def is_stutter_detected(frame_diff, threshold=30):
    # Determine if stutter is detected based on frame difference
    return cv2.countNonZero(frame_diff) > threshold

def load_video(video_path):
    # Load video from the specified path
    return cv2.VideoCapture(video_path)

def release_video_capture(video_capture):
    # Release the video capture object
    video_capture.release()