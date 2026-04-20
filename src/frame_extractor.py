import cv2
import os
import sys

def extract_frames(video_path, output_dir, interval=60):
    video_path = os.path.abspath(video_path)
    if not os.path.exists(video_path):
        print(f"Error: file not found: {video_path}")
        return
    os.makedirs(output_dir, exist_ok=True)
    cap = cv2.VideoCapture(video_path)
    frame_count = 0

    while True:
        success, frame = cap.read()
        if not success:
            break
        if frame_count % interval == 0:
            cv2.imwrite(os.path.join(output_dir, f'frame_{frame_count}.jpg'), frame)
        frame_count += 1

    cap.release()
    print(f"Extracted {frame_count // interval} frames to {output_dir}")

if __name__ == '__main__':
    video_path = sys.argv[1] if len(sys.argv) > 1 else 'footage/session1/DJI_20260406130218_0006_D.MP4'
    session = os.path.splitext(os.path.basename(video_path))[0]
    extract_frames(video_path, os.path.join('frames', session))
