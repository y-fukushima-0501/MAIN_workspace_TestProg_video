# ===============================
# 実行環境（カーネル）はTSTVIDEO_Prog（Python 3.12.11）
# ===============================
import cv2
import threading
import time
import hashlib
import pandas as pd
import os
import tempfile
import shutil
import cupy
import sys
import cupy as cp
from datetime import datetime
from queue import Queue
import matplotlib.pyplot as plt
import matplotlib.font_manager as fm
import psutil
import platform
import psutil
import GPUtil
import tkinter as tk
from tkinter import ttk
import numpy as np

# === 日本語フォント設定 ===
plt.rcParams['font.family'] = 'MS Gothic'
plt.rcParams['axes.unicode_minus'] = False

# ===============================
# 一時フォルダとCuPy環境の安全設定
# ===============================

# すべての環境でASCIIパスを使う
SAFE_TEMP_DIR = r"C:\cupy_temp"
os.makedirs(SAFE_TEMP_DIR, exist_ok=True)

# Windowsの環境変数を一時的に上書き
os.environ["TMP"] = SAFE_TEMP_DIR
os.environ["TEMP"] = SAFE_TEMP_DIR
tempfile.tempdir = SAFE_TEMP_DIR

# CuPyのキャッシュ・インクルードディレクトリを安全パスに設定
CUPY_CACHE_DIR = os.path.join(SAFE_TEMP_DIR, "cupy_cache")
CUPY_INCLUDE_DIR = os.path.join(SAFE_TEMP_DIR, "cupy_include")
os.makedirs(CUPY_CACHE_DIR, exist_ok=True)
os.makedirs(CUPY_INCLUDE_DIR, exist_ok=True)

os.environ["CUPY_CACHE_DIR"] = CUPY_CACHE_DIR
os.environ["CUPY_INCLUDE_PATH"] = CUPY_INCLUDE_DIR

print(f"✅ CuPy cache dir set to: {CUPY_CACHE_DIR}")
print(f"✅ CuPy include dir set to: {CUPY_INCLUDE_DIR}")

# CuPy includeをコピー（ビルド済みexe配下 or site-packagesから）
try:
    if hasattr(sys, "_MEIPASS"):
        base_dir = sys._MEIPASS
    else:
        base_dir = os.path.dirname(os.path.abspath(__file__))

    possible_paths = [
        os.path.join(base_dir, "cupy", "_core", "include", "cupy"),
        os.path.join(sys.prefix, "Lib", "site-packages", "cupy", "_core", "include", "cupy")
    ]
    for p in possible_paths:
        if os.path.exists(p):
            dst = os.path.join(CUPY_INCLUDE_DIR, "cupy")
            if os.path.exists(dst):
                shutil.rmtree(dst)
            shutil.copytree(p, dst)
            print(f"✅ Copied CuPy headers from: {p}")
            break
    else:
        print("⚠ CuPy header files not found, proceeding without copy")
except Exception as e:
    print(f"⚠ Failed to copy CuPy headers: {e}")

# ===============================
# 出力フォルダの作成（デスクトップを避ける）
# ===============================
safe_output_base = os.path.join(os.getcwd(), "CameraCapture_GPU_Output")
os.makedirs(safe_output_base, exist_ok=True)
timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
save_folder = os.path.join(safe_output_base, timestamp)
os.makedirs(save_folder, exist_ok=True)
csv_path = os.path.join(save_folder, "camera_frame_test.csv")

print(f"📁 Output folder: {save_folder}")

# =========================
# スレッドカメラクラス
# =========================
class CameraCapture:
    def __init__(self, device_number=0, width=640, height=480, fps=60): #ここの値はデフォルト値（デフォルト値は「引数を渡さなかったときの初期値」にすぎないため、メインループの引数を変えても影響しない）
        """🎥 スレッドカメラクラス（常に最新フレームを保持）"""
        
        # --- DirectShow を使用してキャプチャ ---
        self.cap = cv2.VideoCapture(device_number, cv2.CAP_DSHOW)
        if not self.cap.isOpened():
            raise RuntimeError("❌ カメラを開けませんでした。")
        
        # --- 基本設定 ---
        self.cap.set(cv2.CAP_PROP_FRAME_WIDTH, width)
        self.cap.set(cv2.CAP_PROP_FRAME_HEIGHT, height)
        self.cap.set(cv2.CAP_PROP_FPS, thread_fps)
        self.cap.set(cv2.CAP_PROP_BUFFERSIZE, 1)

        # --- 自動補正をオフにする ---
        self.cap.set(cv2.CAP_PROP_AUTO_EXPOSURE, 0.25)
        self.cap.set(cv2.CAP_PROP_EXPOSURE, -6)
        self.cap.set(cv2.CAP_PROP_AUTO_WB, 0)
        self.cap.set(cv2.CAP_PROP_WHITE_BALANCE_BLUE_U, 4600)
        self.cap.set(cv2.CAP_PROP_GAIN, 0)

        # --- カメラが実際に設定できたFPS値を取得して保持 ---
        self.fps_set = self.cap.get(cv2.CAP_PROP_FPS)
        
        # --- 内部変数 ---
        self.frame = None
        self.lock = threading.Lock()
        self.running = True

        # --- 更新スレッド開始 ---
        self.thread = threading.Thread(target=self._update, daemon=True)
        self.thread.start()

    def _update(self):
        """常に最新フレームを保持"""
        # --- 初期ウォームアップ（露出・WB安定） ---
        for _ in range(15):
            self.cap.grab()
            time.sleep(0.03)

        while self.running:
            # 最新フレームのみ取得（古いものは破棄）
            got = self.cap.grab()
            if not got:
                time.sleep(0.001)
                continue

            ret, frame = self.cap.retrieve()
            if ret:
                with self.lock:
                    self.frame = frame
            else:
                time.sleep(0.001)

    def read(self):
        """最新フレームをコピーして返す"""
        with self.lock:
            return self.frame.copy() if self.frame is not None else None

    def release(self):
        """キャプチャ終了"""
        self.running = False
        self.thread.join(timeout=1)
        self.cap.release()

# =========================
# GPU処理スレッド
# =========================
class GPUProcessingThread(threading.Thread):
    def __init__(self, queue, save_folder, hash_threshold=5, debug_diff=False):
        super().__init__(daemon=True)
        self.queue = queue
        self.save_folder = save_folder
        self.hash_threshold = hash_threshold
        self.debug_diff = debug_diff
        self.records = []
        self.prev_gray_gpu = None
        self.prev_hash = None
        self.prev_cpu_gray = None
        self.running = True

    def run(self):
        frame_id = 0
        while self.running or not self.queue.empty():
            if self.queue.empty():
                time.sleep(0.001)
                continue

            # --- 最新フレームのみ保持 ---
            frame, timestamp = self.queue.get()
            while not self.queue.empty():
                frame, timestamp = self.queue.get_nowait()

            # --- CPU側でグレースケール化（比較確認用） ---
            frame_gray_cpu = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
            # frame_gray_cpu = cv2.medianBlur(frame_gray_cpu, 3)  # ←必要ならノイズ除去ON

            # --- 2連続フレーム差分デバッグ (デバックを使用したいときに使用 → debug_diff=True)---
            if self.debug_diff and self.prev_cpu_gray is not None:
                diff_cpu = np.abs(frame_gray_cpu.astype(np.int16) - self.prev_cpu_gray.astype(np.int16))
                diff_max = int(diff_cpu.max()) #←最も差が大きかった画素の差
                diff_mean = float(diff_cpu.mean()) #←全体の平均差
                print(f"DBG: diff_max={diff_max}, diff_mean={diff_mean:.2f}")
                if diff_max > 0:
                    cv2.imwrite(os.path.join(self.save_folder, f"dbg_prev_{frame_id-1:04d}.png"), self.prev_cpu_gray)
                    cv2.imwrite(os.path.join(self.save_folder, f"dbg_now_{frame_id:04d}.png"), frame_gray_cpu)
                    np.save(os.path.join(self.save_folder, f"dbg_diff_{frame_id:04d}.npy"), diff_cpu)
            self.prev_cpu_gray = frame_gray_cpu.copy()

            # --- GPUに転送してグレースケール化※GPUでグレースケール化（整数演算で完全一致保証） ---
            frame_gpu = cp.asarray(frame, dtype=cp.uint8)
            gray_gpu = (
                (frame_gpu[..., 2].astype(cp.uint16) * 29 +   # B
                frame_gpu[..., 1].astype(cp.uint16) * 150 +  # G
                frame_gpu[..., 0].astype(cp.uint16) * 77) >> 8
            ).astype(cp.uint8)

            # --- GPUで差分計算 ---
            if self.prev_gray_gpu is not None:
                diff_gpu = cp.abs(gray_gpu.astype(cp.int16) - self.prev_gray_gpu.astype(cp.int16))
                diff_max = int(cp.max(diff_gpu).get())
                diff_flag = "〇" if diff_max > self.hash_threshold else "×"
            else:
                diff_max = 0  # ← 初期化
                diff_flag = "〇"

            # --- ハッシュ計算（CPU側でMD5） ---
            frame_gray_cpu = cp.asnumpy(gray_gpu)
            frame_hash = hashlib.md5(frame_gray_cpu.tobytes()).hexdigest()
            if self.prev_hash is not None:
                same_hash_flag = "〇" if frame_hash == self.prev_hash else "×"
            else:
                same_hash_flag = "×"

            # --- 画像保存 ---
            img_file = f"frame_{frame_id:04d}.jpg"
            cv2.imwrite(os.path.join(self.save_folder, img_file), frame)

            # --- CPU・メモリ使用率取得 ---
            cpu_percent = psutil.cpu_percent(interval=None)
            mem_percent = psutil.virtual_memory().percent           

            # --- 記録 ---
            interval = timestamp - (self.records[-1]["Timestamp_ms"]/1000 if self.records else timestamp)
            fps = 1.0 / interval if interval > 0 else 0.0
            self.records.append({
                "Frame": frame_id,
                "Interval_sec": interval,
                "FPS": fps,
                "DiffFlag": diff_flag,
                "Diff": diff_max,
                "SameHashFlag": same_hash_flag,
                "frame_hash": frame_hash,
                "Timestamp_ms": timestamp*1000,
                "CPU_percent": cpu_percent,
                "Memory_percent": mem_percent,
                "ImageFile": img_file
            })

            # --- 現在値プリント ---
            print(f"[{frame_id:04d}] {interval*1000:6.2f} ms | FPS:{fps:5.2f} | Diff:{diff_flag} | HashSame:{same_hash_flag}")

            # --- 次回用 ---
            self.prev_gray_gpu = gray_gpu
            self.prev_hash = frame_hash
            frame_id += 1

# =========================
# メイン設定（初期値）
# =========================
device_number = 0      # カメラデバイス番号
thread_fps = 30        # カメラスレッド設定FPS
target_fps = 15        # メインループ設定FPS
capture_time = 120     # 撮影時間（秒）
frame_interval = 1.0 / target_fps
limit_frames = capture_time * target_fps  # 撮影時間 × FPS

# =========================
# GUI
# =========================
def apply_settings():
    global device_number, thread_fps, target_fps, frame_interval, limit_frames, capture_time
    device_number = int(device_entry.get())
    thread_fps = int(thread_fps_slider.get())
    target_fps = int(main_fps_slider.get())
    capture_time = int(capture_time_slider.get())  # 撮影時間を取得
    frame_interval = 1.0 / target_fps
    limit_frames = capture_time * target_fps
    print(f"✅ 設定反映: target_fps={target_fps}, 撮影時間={capture_time}秒, limit_frames={limit_frames}")
    root.destroy()  # GUIを閉じる

root = tk.Tk()
root.title("カメラ設定")

# デバイス番号
tk.Label(root, text="デバイス番号").grid(row=0, column=0)
device_entry = tk.Entry(root)
device_entry.insert(0, str(device_number))
device_entry.grid(row=0, column=1)

# カメラスレッドFPS
tk.Label(root, text="カメラスレッドFPS").grid(row=1, column=0)
thread_fps_slider = tk.Scale(root, from_=1, to=60, orient=tk.HORIZONTAL)
thread_fps_slider.set(thread_fps)
thread_fps_slider.grid(row=1, column=1)

# メインループFPS
tk.Label(root, text="メインループFPS").grid(row=2, column=0)
main_fps_slider = tk.Scale(root, from_=1, to=60, orient=tk.HORIZONTAL)
main_fps_slider.set(target_fps)
main_fps_slider.grid(row=2, column=1)

# --- 撮影時間（秒） ---
tk.Label(root, text="撮影時間（秒）").grid(row=3, column=0)
capture_time_slider = tk.Scale(root, from_=10, to=600, orient=tk.HORIZONTAL)  # 10秒〜10分
capture_time_slider.set(capture_time)
capture_time_slider.grid(row=3, column=1)

tk.Button(root, text="適用", command=apply_settings).grid(row=4, column=0, columnspan=2, pady=10)

# GUIを表示して設定を待つ
root.mainloop()

cam = CameraCapture(device_number, fps=thread_fps)
queue = Queue(maxsize=10)
processor = GPUProcessingThread(queue, save_folder)
processor.start()

print(f"🎥 カメラスレッド設定FPS: {thread_fps}")
print(f"🎥 カメラスレッド設定FPS(取得値): {cam.fps_set:.2f}")
print(f"🎥 メインループ設定FPS: {target_fps}")

# =========================
# メインループ
# =========================
frame_id = 0
next_time = time.time()
# start_time = time.time()

try:
    while frame_id < limit_frames:
        now = time.time()
        if now < next_time:
            time.sleep(next_time - now)

        frame = cam.read()
        if frame is None:
            time.sleep(0.001)
            continue

        timestamp = time.time()
        try:
            queue.put_nowait((frame, timestamp))
        except:
            pass

        frame_id += 1
        next_time += frame_interval

except KeyboardInterrupt:
    print("⏹ 中断")

finally:
    cam.release()
    processor.running = False
    processor.join()

    # CSV保存
    df = pd.DataFrame(processor.records)
    df.to_csv(csv_path, index=False, encoding="utf-8-sig")

    # 平均FPS
    if len(processor.records) > 1:
        total_time = (processor.records[-1]["Timestamp_ms"] - processor.records[0]["Timestamp_ms"]) / 1000
        avg_fps = len(processor.records) / total_time
    else:
        avg_fps = 0.0

    # --- システム情報取得 ---
    os_info = platform.platform()
    cpu_info = platform.processor()
    memory = psutil.virtual_memory()
    mem_total_gb = memory.total / (1024 ** 3)  # GB単位

    # GPU情報（複数ある場合は1台目を使用）
    gpus = GPUtil.getGPUs()
    gpu_info = gpus[0].name if gpus else "No GPU"

    # テキスト保存
    txt_path = os.path.join(save_folder, "fps_summary.txt")
    with open(txt_path, "w", encoding="utf-8") as f:
        f.write(f"🎥 カメラスレッド設定FPS: {thread_fps:.2f}\n")
        f.write(f"🎥 カメラスレッド設定FPS（取得値）: {cam.fps_set:.2f}\n")
        f.write(f"⏱ メインループFPS: {target_fps:.2f}\n")
        f.write(f"📈 実測平均FPS: {avg_fps:.2f}\n")
        f.write("\n--- システム情報 ---\n")
        f.write(f"OS: {os_info}\n")
        f.write(f"CPU: {cpu_info}\n")
        f.write(f"メモリ合計: {mem_total_gb:.1f} GB\n")
        f.write(f"GPU: {gpu_info}\n")

    print(f"📈 実測平均FPS: {avg_fps:.2f}")
    print(f"📁 保存フォルダ: {save_folder}")
    print(f"✅ CSV保存完了 : {csv_path}")
    print(f"✅ FPSサマリー保存完了: {txt_path}")

# === CSV読み込み ===
df = pd.read_csv(csv_path)
df["Time_sec"] = (df["Timestamp_ms"] - df["Timestamp_ms"].iloc[0]) / 1000
df["DiffFlag_num"] = df["DiffFlag"].map({"〇": 1, "×": 0})

# === グラフ描画 ===
fig, ax1 = plt.subplots(figsize=(12, 6))

# --- FPSの折れ線グラフ（左軸）---
ax1.plot(df["Time_sec"], df["FPS"], color="tab:blue", label="FPS", linewidth=1.5)
ax1.set_xlabel("Time (s)")
ax1.set_ylabel("FPS", color="tab:blue")
ax1.tick_params(axis="y", labelcolor="tab:blue")
ax1.grid(True, alpha=0.3)
ax1.set_ylim(0, 120)  # 縦軸固定

# --- DiffFlagを右軸で点表示 ---
ax2 = ax1.twinx()
ax2.scatter(df["Time_sec"], df["DiffFlag_num"], color="tab:red", label="DiffFlag", s=20, alpha=0.7)
ax2.set_ylabel("DiffFlag (1=〇, 0=×)", color="tab:red")
ax2.tick_params(axis="y", labelcolor="tab:red")
ax2.set_ylim(0, 1.5)  # 縦軸固定

# --- 凡例とタイトル ---
lines, labels = ax1.get_legend_handles_labels()
lines2, labels2 = ax2.get_legend_handles_labels()
ax1.legend(lines + lines2, labels + labels2, loc="upper right")

plt.title("Frame Rate and Difference Detection Over Time")
plt.tight_layout()

# --- JPEG保存 ---
graph_path = os.path.join(save_folder, "00_frame_rate_diff.jpg")
plt.savefig(graph_path, format="jpeg", dpi=200)
plt.show()

print(f"📁 グラフ保存先: {graph_path}")

# --- CPU/メモリ用のグラフ（縦軸固定0-100%） ---
fig2, ax1 = plt.subplots(figsize=(12, 6))

# CPU使用率（左軸）
ax1.plot(df["Time_sec"], df["CPU_percent"], color="tab:green", label="CPU (%)", linewidth=1.5)
ax1.set_xlabel("Time (s)")
ax1.set_ylabel("CPU (%)", color="tab:green")
ax1.tick_params(axis="y", labelcolor="tab:green")
ax1.set_ylim(0, 100)  # 縦軸固定
ax1.grid(True, alpha=0.3)

# メモリ使用率（右軸）
ax2 = ax1.twinx()
ax2.plot(df["Time_sec"], df["Memory_percent"], color="tab:orange", label="Memory (%)", linewidth=1.5)
ax2.set_ylabel("Memory (%)", color="tab:orange")
ax2.tick_params(axis="y", labelcolor="tab:orange")
ax2.set_ylim(0, 100)  # 縦軸固定

# 凡例統合
lines, labels = ax1.get_legend_handles_labels()
lines2, labels2 = ax2.get_legend_handles_labels()
ax1.legend(lines + lines2, labels + labels2, loc="upper right")

plt.title("CPU and Memory Usage Over Time (0-100%)")
plt.tight_layout()

# JPEG保存
cpu_mem_graph_path = os.path.join(save_folder, "00_cpu_memory_usage_fixed.jpg")
plt.savefig(cpu_mem_graph_path, format="jpeg", dpi=200)
plt.show()

print(f"📁 CPU/メモリグラフ保存先: {cpu_mem_graph_path}")