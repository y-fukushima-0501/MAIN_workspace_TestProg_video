import unittest
from src.detector.processor import process_video
from src.detector.analyzer import analyze_stutter

class TestVideoStutterDetectionIntegration(unittest.TestCase):

    def test_video_processing_and_analysis(self):
        video_path = "path/to/test/video.mp4"
        processed_data = process_video(video_path)
        self.assertIsNotNone(processed_data, "Processed data should not be None")

        stutter_analysis = analyze_stutter(processed_data)
        self.assertIsInstance(stutter_analysis, dict, "Stutter analysis should return a dictionary")
        self.assertIn("stutter_detected", stutter_analysis, "Stutter analysis should contain 'stutter_detected' key")

if __name__ == "__main__":
    unittest.main()