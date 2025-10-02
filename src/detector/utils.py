import cv2

# ===============================================
# フレーム差分計算とカクつき判定用ユーティリティ
# ===============================================

def calculate_frame_difference(frame1, frame2):
    """
    2つのフレーム間の絶対差分を計算する関数

    Parameters:
    frame1, frame2: numpy 配列形式の動画フレーム

    Returns:
    numpy 配列: 各ピクセルの絶対差分
    """
    # OpenCVの absdiff 関数で差分を計算
    return cv2.absdiff(frame1, frame2)


def is_stutter_detected(frame_diff, threshold=30):
    """
    フレーム差分に基づいてカクつきが発生したか判定する関数

    Parameters:
    frame_diff: calculate_frame_difference で得られたフレーム差分
    threshold (int): カクつきと判定する差分の閾値

    Returns:
    bool: 差分が閾値を超えた場合 True（カクつき検出）
    """
    # 差分フレームの非ゼロピクセル数が閾値を超える場合にカクつきと判定
    return cv2.countNonZero(frame_diff) > threshold


def load_video(video_path):
    """
    指定されたパスの動画を読み込む関数

    Parameters:
    video_path (str): 読み込む動画ファイルのパス

    Returns:
    cv2.VideoCapture: OpenCV の動画キャプチャオブジェクト
    """
    return cv2.VideoCapture(video_path)


def release_video_capture(video_capture):
    """
    動画キャプチャオブジェクトを解放する関数

    Parameters:
    video_capture (cv2.VideoCapture): 解放する動画キャプチャオブジェクト
    """
    video_capture.release()
