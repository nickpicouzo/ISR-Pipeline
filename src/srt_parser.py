import re
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path


@dataclass
class SRTFrame:
    frame_num: int
    timestamp: datetime
    diff_time_ms: int
    rel_alt: float
    abs_alt: float
    latitude: float
    longitude: float
    focal_len: float


_TELEMETRY_RE = re.compile(
    r"FrameCnt:\s*(\d+),\s*DiffTime:\s*(\d+)ms\s*\n"
    r"(\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2}\.\d+)\s*\n"
    r".*?\[focal_len:\s*([\d.]+)\]"
    r".*?\[latitude:\s*([-\d.]+)\]"
    r".*?\[longitude:\s*([-\d.]+)\]"
    r".*?\[rel_alt:\s*([-\d.]+)\s+abs_alt:\s*([-\d.]+)\]",
    re.DOTALL,
)


def parse_srt(srt_path: str | Path) -> list[SRTFrame]:
    text = Path(srt_path).read_text(encoding="utf-8")
    frames = []
    for m in _TELEMETRY_RE.finditer(text):
        frame_num, diff_ms, ts_str, focal, lat, lon, rel_alt, abs_alt = m.groups()
        frames.append(SRTFrame(
            frame_num=int(frame_num),
            timestamp=datetime.strptime(ts_str, "%Y-%m-%d %H:%M:%S.%f"),
            diff_time_ms=int(diff_ms),
            rel_alt=float(rel_alt),
            abs_alt=float(abs_alt),
            latitude=float(lat),
            longitude=float(lon),
            focal_len=float(focal),
        ))
    return frames


def get_frame_telemetry(frames: list[SRTFrame], frame_num: int) -> SRTFrame | None:
    """Return telemetry for a specific 1-based frame number."""
    idx = frame_num - 1
    if 0 <= idx < len(frames):
        return frames[idx]
    return None
