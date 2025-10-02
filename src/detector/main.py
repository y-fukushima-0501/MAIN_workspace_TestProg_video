import cv2
import numpy as np
import argparse
import time
import os


# ===============================================
# 動画のカクつき（stutter）を検出する関数
# source: ファイルパスまたはデバイス番号（例: 0）またはデバイス名
# 戻り値: カクつきが発生したフレーム番号のリスト
# 動作: ファイル or キャプチャデバイスの両方に対応
# ===============================================
def detect_stutter(source, diff_thresh=2.0, min_consec=3, max_frames=None, backend=None, record_path=None):
    """
    source: str or int - 動画ファイルパスかカメラデバイス（インデックスまたはDirectShow名）
    diff_thresh: float - グレースケール差分の平均がこれ以下なら「ほぼ同一フレーム」と判定
    min_consec: int - 連続で閾値以下が続いたらカクつきと判断するフレーム数
    max_frames: int|None - ライブキャプチャ時に処理する最大フレーム数（Noneで制限なし、ただし手動で終了可）
    backend: OpenCV backend flag（例: cv2.CAP_DSHOW） - WindowsでDirectShowを使う場面で指定
    record_path: 出力録画パス（省略可）
    """
    # source が数字文字列なら int に変換
    cap = None
    try:
        src = int(source)
    except Exception:
        src = source

    # キャプチャオープン
    if isinstance(src, int):
        if backend is not None:
            cap = cv2.VideoCapture(src, backend)
        else:
            # Windowsでキャプチャボードを使う場合はCAP_DSHOWが安定することが多い
            cap = cv2.VideoCapture(src, cv2.CAP_DSHOW)
    else:
        # ファイルパスやデバイス名（DirectShow文字列など）
        if backend is not None:
            cap = cv2.VideoCapture(src, backend)
        else:
            cap = cv2.VideoCapture(src)

    stutter_frames = []
    frame_count = 0

    if not cap or not cap.isOpened():
        print(f"Error: Could not open source: {source}")
        return stutter_frames

    previous_gray = None
    consec = 0

    writer = None
    if record_path:
        # 出力ファイル用のVideoWriterを準備（入力フレームサイズと同じ設定）
        fourcc = cv2.VideoWriter_fourcc(*'mp4v')

    while True:
        ret, frame = cap.read()
        if not ret:
            # ファイルの終端かキャプチャが切断された
            break

        frame_count += 1

        # VideoWriterがあれば初期化（最初のフレームのサイズを使う）
        if record_path and writer is None:
            h, w = frame.shape[:2]
            writer = cv2.VideoWriter(record_path, fourcc, max(1, cap.get(cv2.CAP_PROP_FPS) or 30), (w, h))

        if writer is not None:
            writer.write(frame)

        # グレースケールで差分を取る
        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        if previous_gray is None:
            previous_gray = gray
            # ライブモードで手動停止したい場合に備え、continue
            if max_frames is not None and frame_count >= max_frames:
                break
            continue

        diff = cv2.absdiff(gray, previous_gray)
        mean_diff = float(np.mean(diff))

        # 閾値以下ならほぼ同じフレーム（スタッターの候補）
        if mean_diff < diff_thresh:
            consec += 1
        else:
            if consec >= min_consec:
                # カクつき区間を記録（終了フレーム番号）
                start = frame_count - consec
                end = frame_count - 1
                stutter_frames.append((start, end))
                print(f"Stutter detected: frames {start} - {end} (mean_diff={mean_diff:.2f})")
            consec = 0

        previous_gray = gray

        # ライブキャプチャで最大フレーム数に達したら終了
        if max_frames is not None and frame_count >= max_frames:
            if consec >= min_consec:
                start = frame_count - consec + 1
                stutter_frames.append((start, frame_count))
            break

    # ループ後の連続カウント処理
    if consec >= min_consec:
        start = frame_count - consec + 1
        stutter_frames.append((start, frame_count))

    if writer is not None:
        writer.release()

    cap.release()
    return stutter_frames


# ===============================================
# スクリプトを直接実行した場合の処理（CLI）
# 使い方の例:
#   python main.py --source 0 --max-frames 500
#   python main.py --source "C:/path/to/video.mp4"
# ===============================================
def _build_cli():
    p = argparse.ArgumentParser(description='Simple video stutter detector (file or capture device).')
    p.add_argument('--source', '-s', default='0', help='Video source. File path or device index (default: 0).')
    p.add_argument('--diff-thresh', type=float, default=2.0, help='Mean diff threshold to consider frames identical')
    p.add_argument('--min-consec', type=int, default=3, help='Minimum consecutive similar frames to mark stutter')
    p.add_argument('--max-frames', type=int, default=None, help='Max frames to process (for live capture)')
    p.add_argument('--record', '-r', default=None, help='Optional path to save processed video (mp4)')
    return p


if __name__ == "__main__":
    parser = _build_cli()
    args = parser.parse_args()

    # source が単純な整数文字列なら int にしてデバイス扱いにする
    src = args.source
    try:
        # 整数変換して失敗しなければデバイス番号として扱う
        int(src)
    except Exception:
        pass

    print(f"Opening source: {src}")
    start = time.time()
    results = detect_stutter(src, diff_thresh=args.diff_thresh, min_consec=args.min_consec, max_frames=args.max_frames, record_path=args.record)
    elapsed = time.time() - start

    if results:
        print(f"Stutter detected at intervals: {results}")
    else:
        print("No stutter detected.")
    print(f"Processed in {elapsed:.2f}s")
