import argparse
from detector.processor import process_video  # 動画の前処理関数
from detector.analyzer import analyze_stutter  # カクつき解析関数

# ===============================================
# CLI（コマンドラインインターフェース）用のメイン関数
# ===============================================
def main():
    # -----------------------------------------------
    # 引数パーサーを作成
    # -----------------------------------------------
    parser = argparse.ArgumentParser(description='Video Stutter Detector CLI')
    
    # 必須引数: 分析対象の動画ファイルパス
    parser.add_argument(
        'video_path', 
        type=str, 
        help='Path to the video file to analyze'
    )
    
    # 任意引数: 分析結果を保存するファイルパス（デフォルトは output.json）
    parser.add_argument(
        '--output', 
        type=str, 
        default='output.json', 
        help='Path to save the analysis results'
    )
    
    # コマンドライン引数の解析
    args = parser.parse_args()
    
    # -----------------------------------------------
    # 動画処理
    # -----------------------------------------------
    print(f'Processing video: {args.video_path}')
    stutter_data = process_video(args.video_path)  # 動画からフレーム情報やカクつきデータを取得
    
    # -----------------------------------------------
    # カクつき解析
    # -----------------------------------------------
    print('Analyzing stutter...')
    analysis_results = analyze_stutter(stutter_data)  # カクつきの検出・解析を実行
    
    # -----------------------------------------------
    # 結果をファイルに保存
    # -----------------------------------------------
    with open(args.output, 'w') as f:
        f.write(analysis_results)
    
    print(f'Analysis results saved to: {args.output}')

# ===============================================
# このスクリプトが直接実行された場合に main() を呼び出す
# ===============================================
if __name__ == '__main__':
    main()
