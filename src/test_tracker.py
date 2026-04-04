import cv2
import sys
import os
from tracker import VehicleTracker


def test(video_path, save_output):
    tracker = VehicleTracker()
    cap = cv2.VideoCapture(video_path)

    if not cap.isOpened():
        print(f"Error: could not open video at {video_path}")
        sys.exit(1)

    writer = None
    if save_output:
        width  = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
        height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
        fps    = cap.get(cv2.CAP_PROP_FPS)
        output_path = os.path.join(
            os.path.dirname(__file__),
            "..", "outputs", "annotated_video", "test_output.mp4"
        )
        writer = cv2.VideoWriter(
            output_path,
            cv2.VideoWriter_fourcc(*"mp4v"),
            fps,
            (width, height),
        )
        print(f"Recording to: {os.path.abspath(output_path)}")

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

        if writer:
            writer.write(frame)

        cv2.imshow("Tracker Test", frame)
        print(f"Frame {frame_count}: {len(tracks)} active tracks")

        # Press Q to quit
        if cv2.waitKey(1) & 0xFF == ord("q"):
            break

    cap.release()
    if writer:
        writer.release()
        print("Output saved.")
    cv2.destroyAllWindows()


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python test_tracker.py <path_to_video>")
        sys.exit(1)

    answer = input("Save annotated output video? (y/n): ").strip().lower()
    save_output = answer == "y"

    test(sys.argv[1], save_output)
