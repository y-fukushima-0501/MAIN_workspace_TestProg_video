import cv2
import numpy as np

def detect_stutter(video_path):
    cap = cv2.VideoCapture(video_path)
    frame_count = 0
    stutter_frames = []

    if not cap.isOpened():
        print("Error: Could not open video.")
        return stutter_frames

    while True:
        ret, frame = cap.read()
        if not ret:
            break

        frame_count += 1

        # Simple stutter detection logic (placeholder)
        if frame_count > 1:
            # Compare current frame with the previous frame
            if np.array_equal(frame, previous_frame):
                stutter_frames.append(frame_count)

        previous_frame = frame

    cap.release()
    return stutter_frames

if __name__ == "__main__":
    video_path = "path/to/your/video.mp4"  # Change this to your video file path
    stutter_frames = detect_stutter(video_path)
    if stutter_frames:
        print(f"Stutter detected at frames: {stutter_frames}")
    else:
        print("No stutter detected.")