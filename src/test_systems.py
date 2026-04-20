"""
Integration test: runs tracker + SRT parser + speed estimator + zone logic
on the first N frames of real footage and prints results to console.

Usage:
    python src/test_systems.py <video.mp4> <srt.SRT> [zones.json] [--frames N]
"""
import argparse
import sys
from pathlib import Path

import cv2

sys.path.insert(0, str(Path(__file__).parent.parent))

from src.tracker import VehicleTracker
from src.srt_parser import parse_srt, get_frame_telemetry
from src.speed_estimator import estimate_speed, centroid_displacement
from src.zone_logic import load_zones, ZoneTracker


def centroid(bbox):
    return ((bbox[0] + bbox[2]) / 2, (bbox[1] + bbox[3]) / 2)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("video")
    parser.add_argument("srt")
    parser.add_argument("zones", nargs="?", default=None)
    parser.add_argument("--frames", type=int, default=150)
    args = parser.parse_args()

    print(f"Loading SRT: {args.srt}")
    srt_frames = parse_srt(args.srt)
    print(f"  {len(srt_frames)} frames parsed")

    zones = load_zones(args.zones) if args.zones else []
    zone_tracker = ZoneTracker(zones)
    print(f"  {len(zones)} zone(s) loaded: {[z.name for z in zones]}")

    print("Loading tracker...")
    tracker = VehicleTracker()

    cap = cv2.VideoCapture(args.video)
    frame_width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
    print(f"  Frame width: {frame_width}px\n")

    prev_bboxes: dict[int, list] = {}
    frame_num = 0

    print(f"{'Frame':>6}  {'ID':>4}  {'Class':<12}  {'Speed (mph)':>11}  {'Zones'}")
    print("-" * 60)

    while frame_num < args.frames:
        ret, frame = cap.read()
        if not ret:
            break
        frame_num += 1

        tracks = tracker.update(frame)
        telemetry = get_frame_telemetry(srt_frames, frame_num)

        for t in tracks:
            tid = t["track_id"]
            bbox = t["bbox"]
            cx, cy = centroid(bbox)

            # Speed
            speed_str = "  —"
            if tid in prev_bboxes and telemetry:
                disp = centroid_displacement(prev_bboxes[tid], bbox)
                spd = estimate_speed(disp, frame_width, telemetry)
                speed_str = f"{spd['mph']:>11.1f}"

            # Zones
            zone_events = zone_tracker.update(tid, cx, cy, frame_num) if zones else []
            for ev in zone_events:
                print(f"  *** Zone event: Track {tid} {ev.event}ed {ev.zone_name} at frame {frame_num}")
            in_zones = ", ".join(zone_tracker._state.get(tid, set())) or "—"

            print(f"{frame_num:>6}  {tid:>4}  {t['class_name']:<12}  {speed_str}  {in_zones}")
            prev_bboxes[tid] = bbox

    cap.release()
    print("\nDone.")


if __name__ == "__main__":
    main()