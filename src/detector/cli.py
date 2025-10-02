import argparse
from detector.processor import process_video
from detector.analyzer import analyze_stutter

def main():
    parser = argparse.ArgumentParser(description='Video Stutter Detector CLI')
    parser.add_argument('video_path', type=str, help='Path to the video file to analyze')
    parser.add_argument('--output', type=str, default='output.json', help='Path to save the analysis results')
    
    args = parser.parse_args()
    
    print(f'Processing video: {args.video_path}')
    stutter_data = process_video(args.video_path)
    
    print('Analyzing stutter...')
    analysis_results = analyze_stutter(stutter_data)
    
    with open(args.output, 'w') as f:
        f.write(analysis_results)
    
    print(f'Analysis results saved to: {args.output}')

if __name__ == '__main__':
    main()