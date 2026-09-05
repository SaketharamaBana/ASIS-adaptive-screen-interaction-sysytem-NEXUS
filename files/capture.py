"""Threaded webcam capture for the multi-hand tracking pipeline."""

import threading
import time
import cv2


class FrameGrabber(threading.Thread):
    def __init__(self, cam_index: int, width: int, height: int, max_hands: int = 2):
        super().__init__(daemon=True)
        if max_hands < 1:
            raise ValueError("max_hands must be at least 1")
        self.max_hands = max_hands
        self.cap = cv2.VideoCapture(cam_index)
        self.cap.set(cv2.CAP_PROP_FRAME_WIDTH, width)
        self.cap.set(cv2.CAP_PROP_FRAME_HEIGHT, height)

        if not self.cap.isOpened():
            raise RuntimeError(
                "Could not open webcam. Check CAM_INDEX in config.py and "
                "that no other app is using the camera."
            )

        self.latest_frame = None
        self.lock = threading.Lock()
        self.running = True

    def run(self):
        while self.running:
            ok, frame = self.cap.read()
            if not ok:
                time.sleep(0.01)
                continue
            frame = cv2.flip(frame, 1)
            with self.lock:
                self.latest_frame = frame

    def get_frame(self):
        with self.lock:
            return None if self.latest_frame is None else self.latest_frame.copy()

    def stop(self):
        self.running = False
        self.join(timeout=1.0)
        if self.cap.isOpened():
            self.cap.release()
