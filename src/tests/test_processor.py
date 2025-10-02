import unittest
from src.detector.processor import VideoProcessor

class TestVideoProcessor(unittest.TestCase):

    def setUp(self):
        self.processor = VideoProcessor()

    def test_process_video(self):
        # Test processing a sample video
        result = self.processor.process("sample_video.mp4")
        self.assertIsNotNone(result)
        self.assertTrue(result['stutter_detected'])

    def test_process_empty_video(self):
        # Test processing an empty video
        result = self.processor.process("empty_video.mp4")
        self.assertIsNotNone(result)
        self.assertFalse(result['stutter_detected'])

    def test_process_invalid_video(self):
        # Test processing an invalid video file
        with self.assertRaises(ValueError):
            self.processor.process("invalid_video.txt")

if __name__ == '__main__':
    unittest.main()