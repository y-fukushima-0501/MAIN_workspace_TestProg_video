import unittest
from src.detector.processor import VideoProcessor

# ===============================================
# VideoProcessor クラスの単体テスト
# ===============================================
class TestVideoProcessor(unittest.TestCase):

    # 各テスト実行前に呼ばれるセットアップ処理
    def setUp(self):
        self.processor = VideoProcessor()  # VideoProcessor のインスタンスを作成

    # -----------------------------------------------
    # サンプル動画の処理テスト
    # -----------------------------------------------
    def test_process_video(self):
        """
        通常の動画を処理してカクつきが検出されるか確認するテスト
        """
        result = self.processor.process("sample_video.mp4")
        # 処理結果が None でないことを確認
        self.assertIsNotNone(result)
        # カクつきが検出されることを確認
        self.assertTrue(result['stutter_detected'])

    # -----------------------------------------------
    # 空の動画の処理テスト
    # -----------------------------------------------
    def test_process_empty_video(self):
        """
        フレームがない空の動画を処理した場合の挙動を確認するテスト
        """
        result = self.processor.process("empty_video.mp4")
        # 処理結果が None でないことを確認
        self.assertIsNotNone(result)
        # カクつきは検出されないことを確認
        self.assertFalse(result['stutter_detected'])

    # -----------------------------------------------
    # 無効なファイルの処理テスト
    # -----------------------------------------------
    def test_process_invalid_video(self):
        """
        動画以外の無効なファイルを処理した場合に例外が発生するか確認するテスト
        """
        with self.assertRaises(ValueError):
            self.processor.process("invalid_video.txt")

# スクリプトを直接実行した場合にテストを実行
if __name__ == '__main__':
    unittest.main()
