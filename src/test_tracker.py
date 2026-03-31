import cv2
import sys
from tracker import VehicleTracker


def test(video_path):
    tracker = VehicleTracker()
    cap = cv2.VideoCapture(video_path)

    if not cap.isOpened():
        print(f"Error: could not open video at {video_path}")
        sys.exit(1)

    frame_count = 0

    while True:
        ret, frame = cap.read()
        if not ret:
            break

        tracks = tracker.update(frame)
        frame_count += 1

        # Draw bounding boxes and IDs
        for t in tracks:
            x1, y1, x2, y2 = [int(v) for v in t["bbox"]]
            track_id = t["track_id"]
            class_name = t["class_name"]

            cv2.rectangle(frame, (x1, y1), (x2, y2), (0, 255, 0), 2)
            cv2.putText(
                frame,
                f"ID {track_id} {class_name}",
                (x1, y1 - 8),
                cv2.FONT_HERSHEY_SIMPLEX,
                0.6,
                (0, 255, 0),
                2,
            )

        cv2.imshow("Tracker Test", frame)
        print(f"Frame {frame_count}: {len(tracks)} active tracks")

        # Press Q to quit
        if cv2.waitKey(1) & 0xFF == ord("q"):
            break

    cap.release()
    cv2.destroyAllWindows()


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python test_tracker.py <path_to_video>")
        sys.exit(1)

    test(sys.argv[1])
