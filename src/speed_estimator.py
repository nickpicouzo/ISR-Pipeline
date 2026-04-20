import math
from srt_parser import SRTFrame

HFOV_DEG = 84.0  # DJI Mini 5 Pro horizontal FOV


def estimate_speed(
    pixel_displacement: float,
    frame_width: int,
    telemetry: SRTFrame,
) -> dict:
    """
    Estimate vehicle speed from pixel displacement between consecutive frames.

    Args:
        pixel_displacement: Euclidean pixel distance of vehicle centroid between frames
        frame_width: width of the video frame in pixels
        telemetry: SRTFrame for the later of the two frames (provides alt + diff_time)

    Returns:
        {"m_per_s": float, "mph": float} — zero if drone is on the ground
    """
    if telemetry.rel_alt <= 0 or telemetry.diff_time_ms <= 0:
        return {"m_per_s": 0.0, "mph": 0.0}

    hfov_rad = math.radians(HFOV_DEG)
    ground_width_m = 2 * telemetry.rel_alt * math.tan(hfov_rad / 2)

    real_displacement_m = (pixel_displacement / frame_width) * ground_width_m
    time_s = telemetry.diff_time_ms / 1000.0

    speed_mps = real_displacement_m / time_s
    speed_mph = speed_mps * 2.23694

    return {"m_per_s": round(speed_mps, 3), "mph": round(speed_mph, 2)}


def centroid_displacement(bbox1: tuple, bbox2: tuple) -> float:
    """
    Euclidean pixel distance between centroids of two bounding boxes.
    Each bbox is (x1, y1, x2, y2).
    """
    cx1 = (bbox1[0] + bbox1[2]) / 2
    cy1 = (bbox1[1] + bbox1[3]) / 2
    cx2 = (bbox2[0] + bbox2[2]) / 2
    cy2 = (bbox2[1] + bbox2[3]) / 2
    return math.hypot(cx2 - cx1, cy2 - cy1)