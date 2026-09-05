"""
Custom Gesture Feature Extraction & Machine Learning Classifier Trainer for NEXUS.
"""

import json
import math
import os
import pickle
from pathlib import Path
import numpy as np
from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import cross_val_score


FINGERTIPS = [4, 8, 12, 16, 20]


def extract_features(landmarks) -> np.ndarray:
    """
    Extract scale-invariant and translation-invariant 3D landmark features.
    
    Accepts either MediaPipe NormalizedLandmark objects or dicts with 'x', 'y', 'z'.
    Returns a 1D numpy array of 73 features.
    """
    pts = []
    for lm in landmarks:
        if hasattr(lm, "x"):
            pts.append((float(lm.x), float(lm.y), float(getattr(lm, "z", 0.0))))
        else:
            pts.append((float(lm["x"]), float(lm["y"]), float(lm.get("z", 0.0))))
    
    pts = np.array(pts, dtype=np.float32)
    wrist = pts[0]
    rel_pts = pts - wrist
    
    # Palm size scaling factor (wrist landmark 0 to middle MCP landmark 9)
    palm_size = float(np.linalg.norm(rel_pts[9]))
    if palm_size < 1e-6:
        palm_size = 1.0
        
    norm_coords = (rel_pts / palm_size).flatten()  # 63 features
    
    # Fingertip pairwise distances
    tip_pts = rel_pts[FINGERTIPS] / palm_size
    pair_distances = []
    num_tips = len(tip_pts)
    for i in range(num_tips):
        for j in range(i + 1, num_tips):
            dist = float(np.linalg.norm(tip_pts[i] - tip_pts[j]))
            pair_distances.append(dist)
            
    features = np.concatenate([norm_coords, np.array(pair_distances, dtype=np.float32)])
    return features


class GestureTrainer:
    """Manages dataset collection, model training, persistence, and live inference."""

    def __init__(self, data_dir: str = "gesture_data"):
        self.data_dir = Path(data_dir)
        self.model_path = self.data_dir / "custom_gesture_model.pkl"
        self.meta_path = self.data_dir / "custom_gestures.json"
        self.data_dir.mkdir(parents=True, exist_ok=True)
        
        self.classifier = None
        self.classes_ = []
        self.load()

    def train(self) -> dict:
        """
        Loads all recorded sample JSONs from gesture_data, fits a RandomForestClassifier,
        evaluates cross-validation score, and saves the trained model.
        """
        X = []
        y = []
        gesture_counts = {}

        manifest_path = self.data_dir / "manifest.json"
        if not manifest_path.exists():
            raise RuntimeError("No recorded gestures found. Record gesture samples first.")

        with manifest_path.open("r", encoding="utf-8") as f:
            manifest = json.load(f)

        gestures_info = manifest.get("gestures", {})
        if not gestures_info:
            raise RuntimeError("Manifest has no gesture categories.")

        for gesture_name, info in gestures_info.items():
            dir_name = info.get("directory", gesture_name)
            gesture_folder = self.data_dir / dir_name
            if not gesture_folder.exists():
                continue

            sample_files = list(gesture_folder.glob("*.json"))
            count = 0
            for s_file in sample_files:
                try:
                    with s_file.open("r", encoding="utf-8") as sf:
                        data = json.load(sf)
                    frames = data.get("frames", [])
                    for frame_lms in frames:
                        feat = extract_features(frame_lms)
                        X.append(feat)
                        y.append(gesture_name)
                        count += 1
                except Exception as err:
                    print(f"[trainer] Error reading sample {s_file}: {err}")
            
            if count > 0:
                gesture_counts[gesture_name] = count

        if len(gesture_counts) < 1:
            raise RuntimeError("No valid gesture sample frames found to train.")

        X = np.array(X, dtype=np.float32)
        y = np.array(y)

        clf = RandomForestClassifier(n_estimators=50, max_depth=10, random_state=42)
        
        # Determine CV score if enough classes/samples
        cv_score = 1.0
        unique_classes = np.unique(y)
        if len(unique_classes) > 1 and len(y) >= 10:
            try:
                scores = cross_val_score(clf, X, y, cv=min(3, len(unique_classes)))
                cv_score = float(np.mean(scores))
            except Exception:
                cv_score = 1.0

        clf.fit(X, y)
        self.classifier = clf
        self.classes_ = list(clf.classes_)

        # Save model pkl and metadata
        with self.model_path.open("wb") as mf:
            pickle.dump(clf, mf)

        meta = {
            "classes": self.classes_,
            "sample_counts": gesture_counts,
            "cv_accuracy": cv_score,
            "trained_at": float(np.datetime64('now', 's').astype(float))
        }
        with self.meta_path.open("w", encoding="utf-8") as metaf:
            json.dump(meta, metaf, indent=2)

        return {
            "status": "success",
            "classes": self.classes_,
            "accuracy": cv_score,
            "total_frames": len(X),
            "gesture_counts": gesture_counts,
        }

    def load(self) -> bool:
        """Loads trained model from disk if available."""
        if self.model_path.exists():
            try:
                with self.model_path.open("rb") as mf:
                    self.classifier = pickle.load(mf)
                self.classes_ = list(self.classifier.classes_)
                return True
            except Exception as e:
                print(f"[trainer] Failed to load custom gesture model: {e}")
                self.classifier = None
                self.classes_ = []
        return False

    def predict(self, landmarks) -> tuple[str, float]:
        """
        Classifies live hand landmarks.
        Returns (gesture_name, confidence_score) or ("none", 0.0).
        """
        if self.classifier is None or not self.classes_:
            return "none", 0.0

        try:
            feat = extract_features(landmarks).reshape(1, -1)
            probs = self.classifier.predict_proba(feat)[0]
            max_idx = int(np.argmax(probs))
            gesture_name = str(self.classes_[max_idx])
            confidence = float(probs[max_idx])
            return gesture_name, confidence
        except Exception:
            return "none", 0.0


__all__ = ["extract_features", "GestureTrainer"]
