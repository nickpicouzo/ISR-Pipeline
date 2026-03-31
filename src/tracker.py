from deep_sort_realtime.deepsort_tracker import DeepSort
from ultralytics import YOLO


class VehicleTracker:
    def __init__(self, model_path="yolo11s.pt", max_age=30, min_hits=3, conf=0.1):
        """
        model_path : path to YOLO11 model weights
        max_age    : frames to keep a track alive without a matching detection
        min_hits   : detections required before a track is confirmed
        """
        self.model = YOLO(model_path)
        self.tracker = DeepSort(max_age=max_age, n_init=min_hits)
        self.conf = conf

        # COCO class IDs for vehicles
        self.vehicle_classes = {
            2: "car",
            3: "motorcycle",
            5: "bus",
            7: "truck",
        }

    def detect(self, frame):
        """
        Run YOLO11 on a frame and return detections in DeepSORT format.
        Each detection: ([left, top, width, height], confidence, class_name)
        """
        results = self.model(frame, verbose=False, conf=self.conf)[0]
        detections = []

        for box in results.boxes:
            class_id = int(box.cls[0])
            if class_id not in self.vehicle_classes:
                continue

            confidence = float(box.conf[0])
            x1, y1, x2, y2 = box.xyxy[0].tolist()
            w = x2 - x1
            h = y2 - y1

            detections.append(
                ([x1, y1, w, h], confidence, self.vehicle_classes[class_id])
            )

        return detections

    def update(self, frame):
        """
        Run detection and tracking on a frame.
        Returns a list of active tracks, each with:
          - track_id  : persistent vehicle ID
          - bbox      : [left, top, right, bottom]
          - class_name: vehicle type
        """
        detections = self.detect(frame)
        tracks = self.tracker.update_tracks(detections, frame=frame)

        active_tracks = []
        for track in tracks:
            if not track.is_confirmed():
                continue

            active_tracks.append({
                "track_id": track.track_id,
                "bbox": track.to_ltrb(),
                "class_name": track.get_det_class(),
            })

        return active_tracks
