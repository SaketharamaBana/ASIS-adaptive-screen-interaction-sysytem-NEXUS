"""Record labeled hand-landmark sequences for user-defined gestures."""

import argparse
import json
import re
import tempfile
import time
from datetime import datetime, timezone
from pathlib import Path

import cv2
import mediapipe as mp
from mediapipe.tasks import python as mp_python
from mediapipe.tasks.python import vision as mp_vision

import config
from capture import FrameGrabber


class GestureRecorder:
    """Persist gesture samples and maintain a small human-readable manifest."""

    def __init__(self, data_dir="gesture_data"):
        self.data_dir = Path(data_dir)
        self.manifest_path = self.data_dir / "manifest.json"
        self.data_dir.mkdir(parents=True, exist_ok=True)

    def save_sample(self, gesture_name, landmark_sequence):
        """Save one sequence and return its path."""
        safe_name = self._safe_name(gesture_name)
        if not landmark_sequence:
            raise ValueError("landmark_sequence must contain at least one frame")

        gesture_dir = self.data_dir / safe_name
        gesture_dir.mkdir(parents=True, exist_ok=True)
        timestamp = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%S.%fZ")
        sample_path = gesture_dir / f"{timestamp}.json"
        payload = {
            "gesture": gesture_name.strip(),
            "recorded_at": timestamp,
            "frames": landmark_sequence,
        }
        self._write_json(sample_path, payload)
        self._update_manifest(gesture_name.strip(), safe_name)
        return sample_path

    def list_gestures(self):
        """Return manifest entries, creating an empty manifest when needed."""
        manifest = self._load_manifest()
        return manifest.get("gestures", {})

    def _update_manifest(self, gesture_name, safe_name):
        manifest = self._load_manifest()
        gestures = manifest.setdefault("gestures", {})
        entry = gestures.setdefault(
            gesture_name,
            {"directory": safe_name, "samples": 0},
        )
        entry["directory"] = safe_name
        entry["samples"] = len(list((self.data_dir / safe_name).glob("*.json")))
        manifest["updated_at"] = datetime.now(timezone.utc).isoformat()
        self._write_json(self.manifest_path, manifest)

    def _load_manifest(self):
        if not self.manifest_path.exists():
            return {"version": 1, "gestures": {}}
        try:
            with self.manifest_path.open("r", encoding="utf-8") as handle:
                manifest = json.load(handle)
        except (OSError, json.JSONDecodeError) as error:
            raise RuntimeError(f"Could not read {self.manifest_path}: {error}") from error
        if not isinstance(manifest, dict) or not isinstance(manifest.get("gestures", {}), dict):
            raise RuntimeError(f"Invalid gesture manifest: {self.manifest_path}")
        return manifest

    @staticmethod
    def _safe_name(gesture_name):
        cleaned = re.sub(r"[^a-zA-Z0-9_-]+", "_", gesture_name.strip()).strip("._")
        if not cleaned:
            raise ValueError("Gesture name must contain letters or numbers")
        return cleaned[:80]

    @staticmethod
    def _write_json(path, payload):
        path.parent.mkdir(parents=True, exist_ok=True)
        temporary_path = None
        try:
            with tempfile.NamedTemporaryFile(
                mode="w", encoding="utf-8", dir=path.parent, delete=False
            ) as handle:
                json.dump(payload, handle, indent=2)
                handle.write("\n")
                temporary_path = Path(handle.name)
            temporary_path.replace(path)
        finally:
            if temporary_path is not None and temporary_path.exists():
                temporary_path.unlink()


def _landmarks_to_frame(landmarks):
    return [{"x": float(point.x), "y": float(point.y), "z": float(point.z)} for point in landmarks]


def record_from_camera(recorder, gesture_name, sample_count, frame_count):
    """Run the keypress-based recording flow and return saved sample paths."""
    if not 5 <= sample_count <= 8:
        raise ValueError("sample_count must be between 5 and 8")
    if not 15 <= frame_count <= 20:
        raise ValueError("frame_count must be between 15 and 20")

    from main import ensure_model_downloaded
    ensure_model_downloaded(config.MODEL_PATH, config.MODEL_URL)

    base_options = mp_python.BaseOptions(model_asset_path=config.MODEL_PATH)
    options = mp_vision.HandLandmarkerOptions(
        base_options=base_options,
        num_hands=1,
        min_hand_detection_confidence=0.6,
        min_tracking_confidence=0.6,
    )
    landmarker = mp_vision.HandLandmarker.create_from_options(options)
    grabber = FrameGrabber(config.CAM_INDEX, config.CAM_WIDTH, config.CAM_HEIGHT)
    grabber.start()
    saved_paths = []
    sequence = []

    print("Press SPACE to begin each sample; hold your gesture steady while recording.")
    print("Press q to cancel.")
    try:
        while len(saved_paths) < sample_count:
            frame = grabber.get_frame()
            if frame is None:
                continue
            display = frame.copy()
            cv2.putText(
                display,
                f"{gesture_name}: {len(saved_paths)}/{sample_count} | SPACE=start q=quit",
                (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 0.55, (0, 255, 255), 2,
            )
            cv2.imshow("NEXUS Gesture Recorder", display)
            key = cv2.waitKey(1) & 0xFF
            if key == ord("q"):
                break
            if key != ord(" "):
                continue

            sequence = []
            deadline = time.monotonic() + 3.0
            while len(sequence) < frame_count and time.monotonic() < deadline:
                frame = grabber.get_frame()
                if frame is None:
                    continue
                rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
                image = mp.Image(image_format=mp.ImageFormat.SRGB, data=rgb)
                result = landmarker.detect(image)
                if result.hand_landmarks:
                    sequence.append(_landmarks_to_frame(result.hand_landmarks[0]))
                    for point in result.hand_landmarks[0]:
                        cv2.circle(
                            frame,
                            (int(point.x * frame.shape[1]), int(point.y * frame.shape[0])),
                            4,
                            (0, 255, 0),
                            -1,
                        )
                cv2.putText(
                    frame,
                    f"Recording {len(sequence)}/{frame_count}",
                    (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 0.8, (0, 255, 255), 2,
                )
                cv2.imshow("NEXUS Gesture Recorder", frame)
                key = cv2.waitKey(1) & 0xFF
                if key == ord("q"):
                    return saved_paths

            if len(sequence) == frame_count:
                path = recorder.save_sample(gesture_name, sequence)
                saved_paths.append(path)
                print(f"[recorder] Saved sample {len(saved_paths)}/{sample_count}: {path}")
            else:
                print("[recorder] No complete hand sequence captured; try again.")
    finally:
        grabber.stop()
        landmarker.close()
        cv2.destroyWindow("NEXUS Gesture Recorder")

    return saved_paths


def main():
    parser = argparse.ArgumentParser(description="Record NEXUS custom gesture samples")
    parser.add_argument("name", help="gesture label, for example wave")
    parser.add_argument("--samples", type=int, default=5, help="samples to record (5-8)")
    parser.add_argument("--frames", type=int, default=15, help="frames per sample (15-20)")
    parser.add_argument("--data-dir", default="gesture_data", help="output directory")
    args = parser.parse_args()

    recorder = GestureRecorder(args.data_dir)
    paths = record_from_camera(recorder, args.name, args.samples, args.frames)
    print(f"[recorder] Finished with {len(paths)} saved sample(s).")


if __name__ == "__main__":
    main()
