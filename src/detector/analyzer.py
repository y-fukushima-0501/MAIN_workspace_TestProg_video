import cv2
import numpy as np

class VideoAnalyzer:
    def __init__(self, video_path):
        self.video_path = video_path
        self.cap = cv2.VideoCapture(video_path)

    def analyze_stutter(self):
        frame_count = int(self.cap.get(cv2.CAP_PROP_FRAME_COUNT))
        fps = self.cap.get(cv2.CAP_PROP_FPS)
        stutter_frames = []

        previous_frame = None
        for i in range(frame_count):
            ret, current_frame = self.cap.read()
            if not ret:
                break

            if previous_frame is not None:
                difference = cv2.absdiff(current_frame, previous_frame)
                non_zero_count = np.count_nonzero(difference)

                if non_zero_count < 1000:  # Threshold for stutter detection
                    stutter_frames.append(i)

            previous_frame = current_frame

        self.cap.release()
        return stutter_frames

    def get_stutter_duration(self, stutter_frames):
        if not stutter_frames:
            return 0

        stutter_duration = len(stutter_frames) / self.cap.get(cv2.CAP_PROP_FPS)
        return stutter_duration

# Example usage:
# analyzer = VideoAnalyzer('path_to_video.mp4')
# stutter_frames = analyzer.analyze_stutter()
# duration = analyzer.get_stutter_duration(stutter_frames)
# print(f'Stutter detected in frames: {stutter_frames}')
# print(f'Total stutter duration: {duration} seconds')