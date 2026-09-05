"""
NEXUS - Adaptive Touchless Interaction System

Features:
  - Threaded webcam capture (non-blocking)
  - MediaPipe hand tracking
  - One-Euro filtered cursor smoothing
    - Two-hand tracking with left-hand precision modifier
    - Left click (pinch), right click (thumb+middle pinch),
    drag (held pinch), scroll (thumb+pinky pinch + vertical move)
  - Debug overlay: landmarks, FPS, active gesture, confidence

Run:
  pip install -r requirements.txt
  python main.py

Controls:
  q - quit
  c - reset smoothing filter and gesture state
"""

import sys
import os
import time
import urllib.request

import cv2
import mediapipe as mp
from mediapipe.tasks import python as mp_python
from mediapipe.tasks.python import vision as mp_vision
import pyautogui

import config
from filters import PointOneEuroFilter
from capture import FrameGrabber
from actions import ActionDispatcher
from gestures import GestureState, precision_mode_active, process_landmarks
from fusion import CursorHistory


def ensure_model_downloaded(path: str, url: str):
    if os.path.exists(path):
        return
    print(f"[setup] Downloading hand landmark model to {path} ...")
    urllib.request.urlretrieve(url, path)
    print("[setup] Done.")


def map_to_screen(nx, ny, screen_w, screen_h):
    m = config.ACTIVE_ZONE_MARGIN
    nx = (nx - m) / (1 - 2 * m)
    ny = (ny - m) / (1 - 2 * m)
    nx = min(max(nx, 0.0), 1.0)
    ny = min(max(ny, 0.0), 1.0)
    return nx * screen_w, ny * screen_h


def run_opencv():
    ensure_model_downloaded(config.MODEL_PATH, config.MODEL_URL)

    landmarker = None
    grabber = None
    dispatcher = None
    try:
        base_options = mp_python.BaseOptions(model_asset_path=config.MODEL_PATH)
        options = mp_vision.HandLandmarkerOptions(
            base_options=base_options,
            num_hands=config.MAX_HANDS,
            min_hand_detection_confidence=0.6,
            min_tracking_confidence=0.6,
        )
        landmarker = mp_vision.HandLandmarker.create_from_options(options)

        grabber = FrameGrabber(
            config.CAM_INDEX, config.CAM_WIDTH, config.CAM_HEIGHT, config.MAX_HANDS
        )
        grabber.start()

        dispatcher = ActionDispatcher()
        point_filter = PointOneEuroFilter(
            min_cutoff=config.SMOOTHING_MIN_CUTOFF, beta=config.SMOOTHING_BETA
        )
        gesture_states = {"left": GestureState(), "right": GestureState()}
        cursor_history = CursorHistory(config.FUSION_HISTORY_SECONDS)

        screen_w, screen_h = pyautogui.size()
        fps_history = []
        prev_t = time.time()

        print("[nexus] Running. 'q' to quit, 'c' to recalibrate.")

        while True:
            frame = grabber.get_frame()
            if frame is None:
                time.sleep(0.005)
                continue

            rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            mp_image = mp.Image(image_format=mp.ImageFormat.SRGB, data=rgb)
            result = landmarker.detect(mp_image)

            h, w = frame.shape[:2]
            info = {"gesture": "none", "confidence": 0.0}

            if result.hand_landmarks:
                hands = []
                for index, landmarks in enumerate(result.hand_landmarks):
                    handedness = "right"
                    if index < len(result.handedness):
                        handedness = result.handedness[index][0].category_name.lower()
                    hands.append((handedness, landmarks))

                    color = (255, 160, 0) if handedness == "left" else (0, 255, 0)
                    for lm in landmarks:
                        cv2.circle(
                            frame, (int(lm.x * w), int(lm.y * h)), 4, color, -1
                        )

                left_hand = next((hand for hand in hands if hand[0] == "left"), None)
                right_hand = next((hand for hand in hands if hand[0] == "right"), None)

                precision_active = False
                if left_hand is not None:
                    precision_active, _ = precision_mode_active(left_hand[1])

                if right_hand is not None:
                    landmarks = right_hand[1]
                    index_tip = landmarks[8]
                    sx, sy = point_filter.filter(index_tip.x, index_tip.y)
                    if precision_active:
                        sx = 0.5 + (sx - 0.5) * config.PRECISION_SENSITIVITY
                        sy = 0.5 + (sy - 0.5) * config.PRECISION_SENSITIVITY
                    tx, ty = map_to_screen(sx, sy, screen_w, screen_h)
                    cursor_history.record(tx, ty)
                    dispatcher.move_cursor(tx, ty)
                    info = process_landmarks(
                        landmarks, gesture_states["right"], dispatcher
                    )
                    if precision_active:
                        info["gesture"] = f"precision + {info['gesture']}"
                else:
                    point_filter.reset()
                    gesture_states["right"].reset(dispatcher)

                if left_hand is not None:
                    gesture_states["left"].reset(dispatcher)
            else:
                point_filter.reset()
                for state in gesture_states.values():
                    state.reset(dispatcher)

            now = time.time()
            fps_history.append(1.0 / max(now - prev_t, 1e-6))
            fps_history = fps_history[-30:]
            prev_t = now
            fps = sum(fps_history) / len(fps_history)

            cv2.putText(frame, f"FPS: {fps:.1f}", (10, 30),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.8, (255, 255, 0), 2)
            cv2.putText(frame, f"Gesture: {info['gesture']} ({info['confidence']})",
                        (10, 60), cv2.FONT_HERSHEY_SIMPLEX, 0.8, (0, 200, 255), 2)

            cv2.imshow("NEXUS (debug view)", frame)

            key = cv2.waitKey(1) & 0xFF
            if key == ord("q"):
                break
            elif key == ord("c"):
                point_filter.reset()
                for state in gesture_states.values():
                    state.reset(dispatcher)
                print("[nexus] Reset.")

    finally:
        if grabber is not None:
            grabber.stop()
        if dispatcher is not None:
            dispatcher.shutdown()
        if landmarker is not None:
            landmarker.close()
        cv2.destroyAllWindows()


def main():
    if "--cli" in sys.argv or "--no-gui" in sys.argv:
        return run_opencv()
    else:
        from ui.dashboard import launch_dashboard
        return launch_dashboard()


if __name__ == "__main__":
    main()
