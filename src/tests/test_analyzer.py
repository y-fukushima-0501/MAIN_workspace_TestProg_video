import pytest
from src.detector.analyzer import analyze_video_stutter

# ===============================================
# analyze_video_stutter 関数の単体テスト
# ===============================================
def test_analyze_video_stutter():
    # -----------------------------------------------
    # カクつきがある動画のテスト
    # -----------------------------------------------
    video_path_stutter = "path/to/video_with_stutter.mp4"
    result = analyze_video_stutter(video_path_stutter)
    
    # カクつきが検出されることを確認
    assert result['stutter_detected'] is True
    # カクつきフレームが存在することを確認
    assert result['stutter_frames'] > 0

    # -----------------------------------------------
    # カクつきがない動画のテスト
    # -----------------------------------------------
    video_path_no_stutter = "path/to/video_without_stutter.mp4"
    result = analyze_video_stutter(video_path_no_stutter)
    
    # カクつきが検出されないことを確認
    assert result['stutter_detected'] is False
    # カクつきフレームがゼロであることを確認
    assert result['stutter_frames'] == 0

    # -----------------------------------------------
    # 無効な動画パスのテスト
    # -----------------------------------------------
    video_path_invalid = "path/to/invalid_video.mp4"
    
    # ファイルが存在しない場合に FileNotFoundError が発生することを確認
    with pytest.raises(FileNotFoundError):
        analyze_video_stutter(video_path_invalid)
