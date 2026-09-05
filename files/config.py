"""Central configuration for NEXUS. Edit values here to tune behavior."""

import os

CAM_INDEX = 0
CAM_WIDTH, CAM_HEIGHT = 640, 480
MAX_HANDS = 2

# One-Euro filter tuning
SMOOTHING_MIN_CUTOFF = 0.8
SMOOTHING_BETA = 0.4

# Pinch-to-click
PINCH_THRESHOLD = 0.045
PINCH_COOLDOWN_SEC = 0.35

# Right click: thumb + middle finger pinch
RIGHT_PINCH_THRESHOLD = 0.045
RIGHT_PINCH_COOLDOWN_SEC = 0.4

# Scroll: thumb + pinky pinch held, then move hand up/down
SCROLL_PINCH_THRESHOLD = 0.05
SCROLL_SENSITIVITY = 800  # multiplier from normalized delta-y to scroll units

# Drag: pinch and hold beyond this duration triggers drag mode
DRAG_HOLD_SEC = 0.5

# Screen mapping active zone (camera-frame margin treated as dead space)
ACTIVE_ZONE_MARGIN = 0.15

# Left-hand pinch modifier
PRECISION_SENSITIVITY = 0.35

# Voice + gesture timestamp alignment
FUSION_HISTORY_SECONDS = 3.0
FUSION_TARGET_MAX_AGE_SECONDS = 1.5

# Guardian Mode liveness signals
GUARDIAN_LIVENESS_ENABLED = True
LIVENESS_FACE_MOTION_THRESHOLD = 0.012
LIVENESS_FACE_WINDOW_SECONDS = 1.5
LIVENESS_VOICE_MIN_SECONDS = 0.35
LIVENESS_VOICE_VARIATION_THRESHOLD = 0.04

# Custom User-Defined Gesture Parameters
CUSTOM_GESTURE_ENABLED = True
CUSTOM_GESTURE_COOLDOWN_SEC = 0.8
CUSTOM_GESTURE_CONFIDENCE_THRESHOLD = 0.70
CUSTOM_BINDINGS = {}

BINDINGS_FILE = os.path.join(os.path.dirname(__file__), "gesture_data", "bindings.json")


def load_bindings():
    global CUSTOM_BINDINGS
    if os.path.exists(BINDINGS_FILE):
        try:
            import json
            with open(BINDINGS_FILE, "r", encoding="utf-8") as f:
                CUSTOM_BINDINGS = json.load(f)
        except Exception as e:
            print(f"[config] Failed to load bindings: {e}")
            CUSTOM_BINDINGS = {}


def save_bindings():
    try:
        import json
        os.makedirs(os.path.dirname(BINDINGS_FILE), exist_ok=True)
        with open(BINDINGS_FILE, "w", encoding="utf-8") as f:
            json.dump(CUSTOM_BINDINGS, f, indent=2)
    except Exception as e:
        print(f"[config] Failed to save bindings: {e}")


load_bindings()

MODEL_PATH = os.path.join(os.path.dirname(__file__), "hand_landmarker.task")
MODEL_URL = (
    "https://storage.googleapis.com/mediapipe-models/hand_landmarker/"
    "hand_landmarker/float16/1/hand_landmarker.task"
)
