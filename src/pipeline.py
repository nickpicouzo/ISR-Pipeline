"""
pipeline.py — Full end-to-end ISR pipeline.

Reads a drone .MP4 + matching .SRT file, runs YOLO11 + DeepSORT tracking,
estimates vehicle speeds, detects zone breaches, writes annotated video and CSV log.

Usage:
    python pipeline.py <video.mp4> <telemetry.SRT> [--zones zones.json] [--model ../models/yolo11s.pt]
"""

import argparse
import csv
import os
import sys

import cv2

from srt_parser import parse_srt, get_frame_telemetry
from speed_estimator import estimate_speed, centroid_displacement
from zone_logic import load_zones, ZoneTracker
from tracker import VehicleTracker


def get_centroid(bbox):
    x1, y1, x2, y2 = bbox
    return (x1 + x2) / 2, (y1 + y2) / 2


def iou(bbox1, bbox2):
    x1 = max(bbox1[0], bbox2[0])
    y1 = max(bbox1[1], bbox2[1])
    x2 = min(bbox1[2], bbox2[2])
    y2 = min(bbox1[3], bbox2[3])
    inter = max(0, x2 - x1) * max(0, y2 - y1)
    a1 = (bbox1[2] - bbox1[0]) * (bbox1[3] - bbox1[1])
    a2 = (bbox2[2] - bbox2[0]) * (bbox2[3] - bbox2[1])
    union = a1 + a2 - inter
    return inter / union if union > 0 else 0


def deduplicate_tracks(tracks, max_centroid_dist=80):
    """Remove duplicate tracks whose centroids are within max_centroid_dist pixels — keep the older (lower) track ID."""
    tracks = sorted(tracks, key=lambda t: t["track_id"])
    keep = []
    for t in tracks:
        cx, cy = get_centroid(t["bbox"])
        duplicate = False
        for k in keep:
            kx, ky = get_centroid(k["bbox"])
            if ((cx - kx) ** 2 + (cy - ky) ** 2) ** 0.5 < max_centroid_dist:
                duplicate = True
                break
        if not duplicate:
            keep.append(t)
    return keep


def draw_overlay(frame, tracks, speeds, zone_tracker):
    for t in tracks:
        x1, y1, x2, y2 = [int(v) for v in t["bbox"]]
        track_id = t["track_id"]
        class_name = t["class_name"]
        speed = speeds.get(track_id, {})
        mph = speed.get("mph", 0.0)

        in_zone = zone_tracker.in_any_zone(track_id)
        box_color = (0, 0, 255) if in_zone else (0, 255, 0)
        text_color = (0, 0, 255) if in_zone else (0, 0, 0)

        cv2.rectangle(frame, (x1, y1), (x2, y2), box_color, 2)

        label = f"ID {track_id} {class_name} {mph:.1f}mph"
        cv2.putText(frame, label, (x1, y1 - 12),
                    cv2.FONT_HERSHEY_SIMPLEX, 1.2, text_color, 3)

    return frame


def run(video_path, srt_path, zones_path, model_path):
    # Load telemetry, zones, tracker
    srt_frames = parse_srt(srt_path)
    zones = load_zones(zones_path) if zones_path and os.path.exists(zones_path) else []
    zone_tracker = ZoneTracker(zones)
    tracker = VehicleTracker(model_path=model_path)

    cap = cv2.VideoCapture(video_path)
    if not cap.isOpened():
        print(f"Error: could not open video: {video_path}")
        sys.exit(1)

    width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
    height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
    fps = cap.get(cv2.CAP_PROP_FPS)

    # Output paths
    base_dir = os.path.dirname(__file__)
    video_dir = os.path.join(base_dir, "..", "outputs", "annotated_video")
    csv_dir = os.path.join(base_dir, "..", "outputs", "csv_logs")

    session = input("Which session is this footage from? (1 or 2): ").strip()
    while session not in ("1", "2"):
        session = input("Please enter 1 or 2: ").strip()
    session_tag = f"session{session}"

    trial = 1
    while os.path.exists(os.path.join(csv_dir, f"speed_log_{session_tag}_{trial}.csv")):
        trial += 1

    video_out_path = os.path.join(video_dir, f"pipeline_output_{session_tag}_{trial}.mp4")
    csv_out_path = os.path.join(csv_dir, f"speed_log_{session_tag}_{trial}.csv")

    writer = cv2.VideoWriter(
        video_out_path,
        cv2.VideoWriter_fourcc(*"mp4v"),
        fps,
        (width, height),
    )

    csv_file = open(csv_out_path, "w", newline="")
    csv_writer = csv.writer(csv_file)
    csv_writer.writerow(["frame", "track_id", "class", "mph", "m_per_s", "zone_event"])

    print(f"Processing: {video_path}")
    print(f"Output video: {os.path.abspath(video_out_path)}")
    print(f"Output CSV:   {os.path.abspath(csv_out_path)}")

    prev_bboxes = {}         # track_id -> bbox from previous frame
    speeds = {}              # track_id -> latest smoothed speed dict
    speed_history = {}       # track_id -> list of recent raw speeds
    total_displacement = {}  # track_id -> cumulative pixel displacement
    frame_num = 0
    MIN_DISPLACEMENT = 30    # pixels — tracks that never move this much are filtered out
    SPEED_WINDOW = 7         # frames to average speed over

    while True:
        ret, frame = cap.read()
        if not ret:
            break

        frame_num += 1
        telemetry = get_frame_telemetry(srt_frames, frame_num)

        # Downscale for faster inference, then scale boxes back up
        small = cv2.resize(frame, (1280, 720))
        scale_x = width / 1280
        scale_y = height / 720
        tracks_small = tracker.update(small)
        tracks = []
        for t in tracks_small:
            x1, y1, x2, y2 = t["bbox"]
            t["bbox"] = [x1 * scale_x, y1 * scale_y, x2 * scale_x, y2 * scale_y]
            tracks.append(t)

        for t in tracks:
            track_id = t["track_id"]
            bbox = t["bbox"]
            class_name = t["class_name"]
            cx, cy = get_centroid(bbox)

            # Speed estimation with rolling average
            speed = {"m_per_s": 0.0, "mph": 0.0}
            if track_id in prev_bboxes and telemetry:
                displacement = centroid_displacement(prev_bboxes[track_id], bbox)
                total_displacement[track_id] = total_displacement.get(track_id, 0) + displacement
                raw_speed = estimate_speed(displacement, width, telemetry)
                history = speed_history.setdefault(track_id, [])
                history.append(raw_speed["m_per_s"])
                if len(history) > SPEED_WINDOW:
                    history.pop(0)
                avg_mps = sum(history) / len(history)
                speed = {"m_per_s": round(avg_mps, 3), "mph": round(avg_mps * 2.23694, 1)}
            speeds[track_id] = speed
            prev_bboxes[track_id] = bbox

            # Skip static false positives
            if total_displacement.get(track_id, 0) < MIN_DISPLACEMENT:
                continue

            # Zone detection
            zone_events = zone_tracker.update(track_id, cx, cy, frame_num) if zones else []

            # Log to CSV
            event_str = ";".join(f"{e.zone_name}:{e.event}" for e in zone_events)
            csv_writer.writerow([frame_num, track_id, class_name,
                                  speed["mph"], speed["m_per_s"], event_str])

        active_tracks = [t for t in tracks if total_displacement.get(t["track_id"], 0) >= MIN_DISPLACEMENT]
        active_tracks = deduplicate_tracks(active_tracks)
        frame = draw_overlay(frame, active_tracks, speeds, zone_tracker)
        writer.write(frame)

        display = cv2.resize(frame, (1280, 720))
        cv2.imshow("ISR Pipeline", display)
        print(f"Frame {frame_num}: {len(tracks)} tracks")

        if cv2.waitKey(1) & 0xFF == ord("q"):
            break

    cap.release()
    writer.release()
    csv_file.close()
    cv2.destroyAllWindows()
    print("Done.")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="ISR Pipeline — vehicle tracking and speed estimation.")
    parser.add_argument("video", help="Path to input .MP4 file")
    parser.add_argument("srt", help="Path to matching .SRT telemetry file")
    parser.add_argument("--zones", default=os.path.join(os.path.dirname(__file__), "zones.json"),
                        help="Path to zones.json (default: src/zones.json)")
    parser.add_argument("--model", default="../models/best.pt",
                        help="Path to YOLO model weights (default: ../models/best.pt)")
    args = parser.parse_args()

    run(args.video, args.srt, args.zones, args.model)
