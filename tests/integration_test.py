import unittest
from src.detector.processor import process_video
from src.detector.analyzer import analyze_stutter

# ===============================================
# Video Stutter Detection の統合テスト
# ===============================================
class TestVideoStutterDetectionIntegration(unittest.TestCase):

    # -----------------------------------------------
    # 動画の処理とカクつき解析を組み合わせた統合テスト
    # -----------------------------------------------
    def test_video_processing_and_analysis(self):
        """
        動画を処理し、そのデータを解析してカクつき検出が正しく行われるか確認する
        """
        video_path = "path/to/test/video.mp4"  # テスト用動画ファイルのパス

        # -----------------------------------------------
        # 動画処理の確認
        # -----------------------------------------------
        processed_data = process_video(video_path)
        # 処理結果が None でないことを確認
        self.assertIsNotNone(processed_data, "Processed data should not be None")

        # -----------------------------------------------
        # カクつき解析の確認
        # -----------------------------------------------
        stutter_analysis = analyze_stutter(processed_data)
        # 解析結果が辞書形式であることを確認
        self.assertIsInstance(stutter_analysis, dict, "Stutter analysis should return a dictionary")
        # 'stutter_detected' キーが含まれていることを確認
        self.assertIn("stutter_detected", stutter_analysis, "Stutter analysis should contain 'stutter_detected' key")

# スクリプトを直接実行した場合に統合テストを実行
if __name__ == "__main__":
    unittest.main()
