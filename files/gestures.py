"""
Gesture recognition: turns raw hand landmarks into named gestures with
a confidence score, and tracks pinch/drag state across frames.

Gestures supported:
  - move        : cursor follows index fingertip (always active)
  - left_click  : thumb + index pinch (quick)
  - right_click : thumb + middle pinch (quick)
  - drag        : thumb + index pinch held beyond DRAG_HOLD_SEC
  - scroll      : thumb + pinky pinch held, hand moves up/down
"""

import time
import numpy as np
import config
from trainer import GestureTrainer

# Global trainer instance for live prediction
_gesture_trainer = GestureTrainer()


def get_trainer_instance() -> GestureTrainer:
    return _gesture_trainer


def _dist(a, b) -> float:
    return float(np.hypot(a.x - b.x, a.y - b.y))


class GestureState:
    """Holds cross-frame state needed to distinguish a quick pinch
    (click) from a held pinch (drag) from a different held pinch (scroll)."""

    def __init__(self):
        self.pinch_start_time = None
        self.is_dragging = False
        self.scroll_active = False
        self.scroll_last_y = None
        self.last_left_click = 0.0
        self.last_right_click = 0.0
        self.last_custom_trigger_time = 0.0

    def reset(self, dispatcher=None):
        if self.is_dragging and dispatcher is not None:
            try:
                dispatcher.end_drag()
            except Exception:
                pass
        self.__init__()


def precision_mode_active(landmarks) -> tuple[bool, float]:
    """Return whether a hand is pinching for the precision modifier."""
    pinch_distance = _dist(landmarks[4], landmarks[8])
    confidence = max(0.0, 1.0 - (pinch_distance / config.PINCH_THRESHOLD))
    return pinch_distance < config.PINCH_THRESHOLD, round(confidence, 2)


def process_landmarks(landmarks, state: GestureState, dispatcher):
    """
    landmarks: list of 21 MediaPipe hand landmarks (normalized 0-1 coords)
    state: GestureState instance, persists across calls for this hand
    dispatcher: ActionDispatcher to fire actions into

    Returns: dict with debug info (active gesture name + confidence) for
    the UI/debug overlay to display.
    """
    now = time.time()
    thumb = landmarks[4]
    index = landmarks[8]
    middle = landmarks[12]
    pinky = landmarks[20]

    left_pinch_dist = _dist(thumb, index)
    right_pinch_dist = _dist(thumb, middle)
    scroll_pinch_dist = _dist(thumb, pinky)

    active_gesture = "move"
    confidence = 1.0

    left_pinching = left_pinch_dist < config.PINCH_THRESHOLD
    right_pinching = right_pinch_dist < config.RIGHT_PINCH_THRESHOLD
    scroll_pinching = scroll_pinch_dist < config.SCROLL_PINCH_THRESHOLD

    # --- Scroll: thumb+pinky pinch held, track vertical hand movement ---
    if scroll_pinching:
        active_gesture = "scroll"
        confidence = 1.0 - (scroll_pinch_dist / config.SCROLL_PINCH_THRESHOLD)
        if not state.scroll_active:
            state.scroll_active = True
            state.scroll_last_y = index.y
        else:
            delta_y = state.scroll_last_y - index.y  # up = positive
            scroll_amount = int(delta_y * config.SCROLL_SENSITIVITY)
            if scroll_amount != 0:
                dispatcher.scroll(scroll_amount)
                state.scroll_last_y = index.y
        return {"gesture": active_gesture, "confidence": round(confidence, 2)}
    else:
        state.scroll_active = False
        state.scroll_last_y = None

    # --- Left pinch: click (quick) or drag (held) ---
    if left_pinching:
        active_gesture = "pinch"
        confidence = 1.0 - (left_pinch_dist / config.PINCH_THRESHOLD)

        if state.pinch_start_time is None:
            state.pinch_start_time = now

        held_duration = now - state.pinch_start_time

        if held_duration >= config.DRAG_HOLD_SEC:
            if not state.is_dragging:
                dispatcher.start_drag()
                state.is_dragging = True
            active_gesture = "drag"
    else:
        if state.pinch_start_time is not None:
            held_duration = now - state.pinch_start_time
            if state.is_dragging:
                dispatcher.end_drag()
                state.is_dragging = False
            elif held_duration < config.DRAG_HOLD_SEC:
                # Quick pinch-and-release = a click, gated by cooldown.
                if (now - state.last_left_click) > config.PINCH_COOLDOWN_SEC:
                    dispatcher.left_click()
                    state.last_left_click = now
                    active_gesture = "left_click"
        state.pinch_start_time = None

    # --- Right pinch: right-click ---
    if right_pinching and not left_pinching:
        r_confidence = 1.0 - (right_pinch_dist / config.RIGHT_PINCH_THRESHOLD)
        if (now - state.last_right_click) > config.RIGHT_PINCH_COOLDOWN_SEC:
            dispatcher.right_click()
            state.last_right_click = now
            active_gesture = "right_click"
            confidence = r_confidence

    # --- User-Defined Custom Trained Gesture Evaluation ---
    if active_gesture == "move" and getattr(config, "CUSTOM_GESTURE_ENABLED", True):
        c_name, c_conf = _gesture_trainer.predict(landmarks)
        if c_name != "none" and c_conf >= getattr(config, "CUSTOM_GESTURE_CONFIDENCE_THRESHOLD", 0.70):
            active_gesture = f"custom:{c_name}"
            confidence = c_conf
            if (now - state.last_custom_trigger_time) > getattr(config, "CUSTOM_GESTURE_COOLDOWN_SEC", 0.8):
                state.last_custom_trigger_time = now
                action_bound = config.CUSTOM_BINDINGS.get(c_name)
                if action_bound:
                    dispatcher.execute_custom_action(action_bound)

    return {"gesture": active_gesture, "confidence": round(confidence, 2)}
