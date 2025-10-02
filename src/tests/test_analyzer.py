import pytest
from src.detector.analyzer import analyze_video_stutter

def test_analyze_video_stutter():
    # Test case for a video with stutter
    video_path_stutter = "path/to/video_with_stutter.mp4"
    result = analyze_video_stutter(video_path_stutter)
    assert result['stutter_detected'] is True
    assert result['stutter_frames'] > 0

    # Test case for a video without stutter
    video_path_no_stutter = "path/to/video_without_stutter.mp4"
    result = analyze_video_stutter(video_path_no_stutter)
    assert result['stutter_detected'] is False
    assert result['stutter_frames'] == 0

    # Test case for an invalid video path
    video_path_invalid = "path/to/invalid_video.mp4"
    with pytest.raises(FileNotFoundError):
        analyze_video_stutter(video_path_invalid)