"""
Click points on a reference frame to define zone polygons.
Left-click to add points, right-click to undo, Enter to finish a zone,
'n' to start a new zone, 's' to save, 'q' to quit.
"""
import json
import sys
from pathlib import Path

import cv2
import numpy as np

COLORS = [
    (0, 255, 0), (0, 128, 255), (255, 0, 128),
    (255, 255, 0), (0, 255, 255), (255, 0, 255),
]


def pick_zones(video_path: str, frame_num: int = 30, output_path: str = "zones.json"):
    cap = cv2.VideoCapture(video_path)
    cap.set(cv2.CAP_PROP_POS_FRAMES, frame_num)
    ret, frame = cap.read()
    cap.release()
    if not ret:
        print(f"Could not read frame {frame_num} from {video_path}")
        return

    base_frame = frame.copy()
    zones = []
    current_points = []

    def redraw():
        img = base_frame.copy()
        # Draw completed zones
        for i, zone in enumerate(zones):
            pts = np.array(zone["points"], dtype=np.int32)
            color = COLORS[i % len(COLORS)]
            cv2.polylines(img, [pts], isClosed=True, color=color, thickness=2)
            cv2.fillPoly(img, [pts], (*color, 40))
            cx = int(np.mean(pts[:, 0]))
            cy = int(np.mean(pts[:, 1]))
            cv2.putText(img, zone["name"], (cx - 20, cy),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.7, color, 2)
        # Draw in-progress points
        color = COLORS[len(zones) % len(COLORS)]
        for pt in current_points:
            cv2.circle(img, pt, 5, color, -1)
        if len(current_points) > 1:
            cv2.polylines(img, [np.array(current_points, dtype=np.int32)],
                          isClosed=False, color=color, thickness=2)
        h, w = img.shape[:2]
        cv2.putText(img, f"Zone {len(zones)+1} | {len(current_points)} pts | "
                        f"LClick=add  RClick=undo  Enter=done  N=new  S=save  Q=quit",
                    (10, h - 15), cv2.FONT_HERSHEY_SIMPLEX, 0.55, (255, 255, 255), 1)
        cv2.imshow("Zone Picker", img)

    def mouse_cb(event, x, y, flags, _):
        if event == cv2.EVENT_LBUTTONDOWN:
            current_points.append((x, y))
            redraw()
        elif event == cv2.EVENT_RBUTTONDOWN and current_points:
            current_points.pop()
            redraw()

    cv2.namedWindow("Zone Picker", cv2.WINDOW_NORMAL)
    cv2.setMouseCallback("Zone Picker", mouse_cb)
    redraw()

    while True:
        key = cv2.waitKey(0) & 0xFF
        if key == 13 or key == 10:  # Enter — finish current zone
            if len(current_points) >= 3:
                name = f"zone_{len(zones)+1}"
                zones.append({"name": name, "points": list(current_points)})
                print(f"Saved {name}: {current_points}")
                current_points.clear()
                redraw()
            else:
                print("Need at least 3 points to close a zone.")
        elif key == ord('n'):  # discard current, start fresh
            current_points.clear()
            redraw()
        elif key == ord('s'):  # save all zones
            Path(output_path).write_text(json.dumps(zones, indent=2))
            print(f"Zones written to {output_path}")
        elif key == ord('q'):
            break

    cv2.destroyAllWindows()

    if zones and output_path:
        Path(output_path).write_text(json.dumps(zones, indent=2))
        print(f"Zones written to {output_path}")

    return zones


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python zone_picker.py <video.mp4> [frame_num] [output.json]")
        sys.exit(1)

    video = sys.argv[1]
    frame = int(sys.argv[2]) if len(sys.argv) > 2 else 30
    out = sys.argv[3] if len(sys.argv) > 3 else "zones.json"
    pick_zones(video, frame, out)