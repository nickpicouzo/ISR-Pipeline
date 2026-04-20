import json
from dataclasses import dataclass, field
from pathlib import Path

import cv2
import numpy as np


@dataclass
class Zone:
    name: str
    points: np.ndarray


@dataclass
class ZoneEvent:
    track_id: int
    zone_name: str
    event: str  # "enter" or "exit"
    frame_num: int


def load_zones(json_path: str | Path) -> list[Zone]:
    data = json.loads(Path(json_path).read_text())
    return [Zone(name=z["name"], points=np.array(z["points"], dtype=np.int32)) for z in data]


def centroid_in_zone(cx: float, cy: float, zone: Zone) -> bool:
    return cv2.pointPolygonTest(zone.points, (float(cx), float(cy)), measureDist=False) >= 0


class ZoneTracker:
    """Tracks per-vehicle zone occupancy across frames and emits enter/exit events."""

    def __init__(self, zones: list[Zone]):
        self.zones = zones
        # {track_id: set of zone names currently occupied}
        self._state: dict[int, set[str]] = {}

    def update(self, track_id: int, cx: float, cy: float, frame_num: int) -> list[ZoneEvent]:
        events = []
        prev = self._state.get(track_id, set())
        curr = {z.name for z in self.zones if centroid_in_zone(cx, cy, z)}

        for name in curr - prev:
            events.append(ZoneEvent(track_id, name, "enter", frame_num))
        for name in prev - curr:
            events.append(ZoneEvent(track_id, name, "exit", frame_num))

        self._state[track_id] = curr
        return events

    def remove_track(self, track_id: int):
        self._state.pop(track_id, None)

    def in_any_zone(self, track_id: int) -> bool:
        return bool(self._state.get(track_id))