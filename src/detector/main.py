import cv2
import numpy as np

# ===============================================
# 動画のカクつき（stutter）を検出する関数
# video_path: 解析する動画ファイルのパス
# 戻り値: カクつきが発生したフレーム番号のリスト
# ===============================================
def detect_stutter(video_path):
    # OpenCVで動画を読み込む
    cap = cv2.VideoCapture(video_path)
    frame_count = 0           # 読み込んだフレームのカウント
    stutter_frames = []       # カクつきが発生したフレーム番号のリスト

    # 動画が開けなかった場合のエラー処理
    if not cap.isOpened():
        print("Error: Could not open video.")
        return stutter_frames

    # 前のフレームを保持する変数
    previous_frame = None

    # フレームを1枚ずつ読み込み
    while True:
        ret, frame = cap.read()
        if not ret:  # フレームが読み込めなかったら終了
            break

        frame_count += 1

        # -----------------------------------------------
        # カクつき検出の簡易ロジック
        # 前のフレームと完全に同じ場合をカクつきと判定
        # （実際の解析ではもっと高度な差分解析が必要）
        # -----------------------------------------------
        if frame_count > 1:
            if np.array_equal(frame, previous_frame):
                stutter_frames.append(frame_count)

        # 次フレームとの比較用に前のフレームを保持
        previous_frame = frame

    # 動画ファイルを閉じる
    cap.release()
    return stutter_frames

# ===============================================
# スクリプトを直接実行した場合の処理
# ===============================================
if __name__ == "__main__":
    video_path = "path/to/your/video.mp4"  # 解析する動画ファイルのパスに変更
    stutter_frames = detect_stutter(video_path)

    # 結果の表示
    if stutter_frames:
        print(f"Stutter detected at frames: {stutter_frames}")
    else:
        print("No stutter detected.")
