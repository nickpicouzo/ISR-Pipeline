# ISR Pipeline
Aerial vehicle detection, tracking, and speed estimation using DJI drone footage of US1, Coral Gables, FL.

## Overview
Nadir drone footage is processed through a three-stage pipeline:
1. **Detection** — YOLO11 (fine-tuned on VisDrone) detects vehicles (car, truck) in each frame
2. **Tracking** — DeepSORT assigns persistent IDs to each vehicle across frames using a Kalman filter
3. **Speed Estimation** — Vehicle speed is calculated in m/s using pixel displacement and drone altitude from SRT telemetry

Final output is an annotated .mp4 with bounding boxes, vehicle IDs, speed overlays, and zone breach alerts, plus CSV logs of all measurements.

## Team
| Name | Role | Owns |
|------|------|------|
| David | Tracking Lead | DeepSORT integration, OpenCV overlay, annotated video |
| Nick | Systems Lead | SRT parser, speed formula, zone logic, drone ops |
| Dylan | ML Lead | Roboflow labeling, YOLO11 fine-tuning, evaluation |

## Setup
See [setup.md](setup.md) for full environment setup instructions.

```bash
# 1. Create and activate virtual environment
python -m venv venv
venv\Scripts\activate

# 2. Install PyTorch — see setup.md for machine-specific command

# 3. Install remaining dependencies
pip install -r requirements.txt

# 4. Verify GPU
python -c "import torch; print(torch.cuda.is_available()); print(torch.cuda.get_device_name(0))"
```

## Running the Tracker
```bash
# Activate virtual environment
venv\Scripts\activate

# Run tracker on a video
cd src
python test_tracker.py "path\to\video.mp4"
```

When prompted, type `y` to save an annotated .mp4 to `outputs/annotated_video/`, or `n` to just preview in a window. Press `Q` to quit.

## Repo Structure
```
ISR-Pipeline/
├── footage/        # Raw drone .MP4 and .SRT files
├── frames/         # Extracted frames for labeling
├── labels/         # Roboflow annotation exports
├── models/         # YOLO11 model weights (.pt)
├── notebooks/      # Colab training notebooks
├── outputs/
│   ├── annotated_video/   # Annotated .mp4 output
│   └── csv_logs/          # Speed and zone breach logs
├── src/            # Python source code
└── matlab/         # Week 4 statistical analysis scripts
```
