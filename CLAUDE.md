# ISR Pipeline — Claude Instructions

## Project Overview
Aerial vehicle detection and speed estimation system using DJI drone footage of US1, Coral Gables, FL. Detects and tracks vehicles using YOLO11 + DeepSORT, estimates speed from pixel displacement and drone altitude.

## Team
- **David** (Tracking Lead) — DeepSORT integration, OpenCV overlay, annotated video output
- **Nick** (Systems Lead) — SRT parser, speed formula, zone logic, drone ops, integration
- **Dylan** (ML Lead) — Roboflow labeling, YOLO11 fine-tuning, evaluation metrics

## Machines
- **David** — Surface Studio, RTX 4050, CUDA 12.1, Python 3.14
- **Nick** — Legion Pro, RTX 5070, CUDA 12.8, Python 3.12

## Environment Setup
```bash
# Activate virtual environment (run from repo root)
venv\Scripts\activate

# Install dependencies (after PyTorch is installed separately)
pip install -r requirements.txt

# Verify GPU
python -c "import torch; print(torch.cuda.is_available()); print(torch.cuda.get_device_name(0))"
```

See `setup.md` for full machine-specific PyTorch install commands.

## Repo Structure
- `footage/` — raw .MP4 and .SRT drone files, split by session
- `frames/` — extracted frames for Roboflow labeling, split by session
- `labels/` — Roboflow exported annotation files
- `models/` — YOLO11 .pt weight files (gitignored)
- `outputs/annotated_video/` — final annotated .mp4 output
- `outputs/csv_logs/` — speed and zone breach CSVs
- `src/` — all Python source code
- `matlab/` — Week 4 MATLAB analysis scripts

## Source Files
- `src/tracker.py` — VehicleTracker class, wraps YOLO11 + DeepSORT
- `src/test_tracker.py` — standalone test script for tracker
- `src/frame_extractor.py` — OpenCV frame extraction (Nick)
- `src/srt_parser.py` — DJI SRT telemetry parser (Nick)
- `src/speed_estimator.py` — speed formula implementation (Nick)
- `src/zone_logic.py` — zone breach detection (Nick)
- `src/pipeline.py` — full end-to-end pipeline

## Key Notes
- `.mp4`, `.SRT`, and `.pt` files are gitignored — too large for GitHub
- `venv/` is gitignored — each teammate generates their own
- Session 2 footage is held out — do not use for training, only evaluation in Week 3
- Current model: `yolo11s.pt` with `conf=0.1` — will be swapped for Dylan's fine-tuned model
- Speed formula: `speed = (pixel_displacement / frame_width) x (altitude x tan(FOV/2) x 2) x fps`

## Running the Tracker
```bash
venv\Scripts\activate
cd src
python test_tracker.py "path\to\video.mp4"
```
