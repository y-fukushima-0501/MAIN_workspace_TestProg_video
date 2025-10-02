import cv2
import numpy as np

# ===============================================
# VideoAnalyzer クラス
# 動画ファイルを解析してカクつき（stutter）を検出する
# ===============================================
class VideoAnalyzer:
    # コンストラクタ
    # video_path: 解析する動画ファイルのパス
    def __init__(self, video_path):
        self.video_path = video_path
        self.cap = cv2.VideoCapture(video_path)  # OpenCVで動画を読み込む

    # -----------------------------------------------
    # カクつきフレームを検出するメソッド
    # 戻り値: カクつきが検出されたフレーム番号のリスト
    # -----------------------------------------------
    def analyze_stutter(self):
        # 動画の総フレーム数を取得
        frame_count = int(self.cap.get(cv2.CAP_PROP_FRAME_COUNT))
        # 動画のFPS（フレーム/秒）を取得
        fps = self.cap.get(cv2.CAP_PROP_FPS)
        stutter_frames = []

        previous_frame = None
        for i in range(frame_count):
            ret, current_frame = self.cap.read()
            if not ret:
                break  # フレーム読み込みに失敗したら終了

            if previous_frame is not None:
                # 現在フレームと前フレームの差分を計算
                difference = cv2.absdiff(current_frame, previous_frame)
                # 差分があるピクセル数をカウント
                non_zero_count = np.count_nonzero(difference)

                # 差分が少ない場合はカクつきと判定
                # （この閾値は動画サイズや内容に応じて調整可能）
                if non_zero_count < 1000:
                    stutter_frames.append(i)

            previous_frame = current_frame  # 次フレームとの比較用に保持

        self.cap.release()  # 動画ファイルを閉じる
        return stutter_frames

    # -----------------------------------------------
    # カクつきの合計時間を計算するメソッド
    # stutter_frames: analyze_stutterで返されたフレーム番号リスト
    # 戻り値: カクつきの合計秒数
    # -----------------------------------------------
    def get_stutter_duration(self, stutter_frames):
        if not stutter_frames:
            return 0

        # 合計フレーム数をFPSで割って秒数を算出
        stutter_duration = len(stutter_frames) / self.cap.get(cv2.CAP_PROP_FPS)
        return stutter_duration

# ===============================================
# 使い方の例
# ===============================================
# analyzer = VideoAnalyzer('path_to_video.mp4')
# stutter_frames = analyzer.analyze_stutter()
# duration = analyzer.get_stutter_duration(stutter_frames)
# print(f'Stutter detected in frames: {stutter_frames}')
# print(f'Total stutter duration: {duration} seconds')
