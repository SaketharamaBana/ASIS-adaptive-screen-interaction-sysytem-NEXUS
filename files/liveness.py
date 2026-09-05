"""Local liveness signals for Guardian Mode.

These checks raise the bar against casual static-photo or silent-replay spoofing;
they are not identity verification and are not defeat-proof against a determined
attacker with a sophisticated replay or presentation attack.
"""

import math
import time
from collections import deque
from dataclasses import dataclass

import numpy as np


@dataclass(frozen=True)
class LivenessResult:
    live: bool
    score: float
    reason: str


class FaceLivenessChecker:
    """Detect natural face motion and optional blink events over a short window."""

    def __init__(
        self,
        motion_threshold=0.012,
        window_seconds=1.5,
        required_frames=4,
    ):
        if motion_threshold <= 0 or window_seconds <= 0 or required_frames < 2:
            raise ValueError("invalid face liveness settings")
        self.motion_threshold = motion_threshold
        self.window_seconds = window_seconds
        self.required_frames = required_frames
        self._frames = deque()
        self._blink_seen = False

    def update(self, landmarks, timestamp=None, blink=False):
        """Add normalized face landmarks and return the current liveness result."""
        if not landmarks:
            return LivenessResult(False, 0.0, "no face landmarks")
        now = time.monotonic() if timestamp is None else timestamp
        points = np.asarray([(point.x, point.y) for point in landmarks], dtype=float)
        self._frames.append((now, points))
        cutoff = now - self.window_seconds
        while self._frames and self._frames[0][0] < cutoff:
            self._frames.popleft()
        self._blink_seen = self._blink_seen or blink

        if len(self._frames) < self.required_frames:
            return LivenessResult(False, 0.0, "collecting face motion")

        first = self._frames[0][1]
        latest = self._frames[-1][1]
        motion = float(np.mean(np.linalg.norm(latest - first, axis=1)))
        motion_score = min(motion / self.motion_threshold, 1.0)
        if self._blink_seen:
            return LivenessResult(True, 1.0, "blink detected")
        if motion >= self.motion_threshold:
            return LivenessResult(True, round(motion_score, 2), "natural face motion detected")
        return LivenessResult(False, round(motion_score, 2), "insufficient face motion")

    def reset(self):
        self._frames.clear()
        self._blink_seen = False


class BlinkDetector:
    """Detect a blink from an eye-aspect-ratio stream supplied by face tracking."""

    def __init__(self, closed_threshold=0.19, open_threshold=0.23):
        if closed_threshold >= open_threshold:
            raise ValueError("closed_threshold must be below open_threshold")
        self.closed_threshold = closed_threshold
        self.open_threshold = open_threshold
        self._closed = False

    def update(self, eye_aspect_ratio):
        """Return True once an eye closes and subsequently opens."""
        if eye_aspect_ratio <= self.closed_threshold:
            self._closed = True
            return False
        blink = self._closed and eye_aspect_ratio >= self.open_threshold
        if blink:
            self._closed = False
        return blink

    def reset(self):
        self._closed = False


class VoiceLivenessChecker:
    """Check that a wake-word clip contains live-varying audio energy.

    This is a replay-resistance signal, not speaker authentication. It should
    be combined with a local speaker verifier when Guardian has one enrolled.
    """

    def __init__(self, min_seconds=0.35, min_energy_variation=0.04):
        if min_seconds <= 0 or min_energy_variation <= 0:
            raise ValueError("invalid voice liveness settings")
        self.min_seconds = min_seconds
        self.min_energy_variation = min_energy_variation

    def check(self, samples, sample_rate):
        """Return whether PCM samples contain sufficient natural variation."""
        audio = np.asarray(samples, dtype=float).reshape(-1)
        if sample_rate <= 0 or len(audio) < sample_rate * self.min_seconds:
            return LivenessResult(False, 0.0, "voice clip too short")
        if not np.any(audio):
            return LivenessResult(False, 0.0, "voice clip is silent")

        window_size = max(int(sample_rate * 0.05), 1)
        usable_size = len(audio) - (len(audio) % window_size)
        windows = audio[:usable_size].reshape(-1, window_size)
        energy = np.sqrt(np.mean(np.square(windows), axis=1))
        variation = float(np.std(energy) / max(np.mean(energy), 1e-8))
        score = min(variation / self.min_energy_variation, 1.0)
        if variation >= self.min_energy_variation:
            return LivenessResult(True, round(score, 2), "voice energy variation detected")
        return LivenessResult(False, round(score, 2), "insufficient voice variation")


__all__ = [
    "BlinkDetector",
    "FaceLivenessChecker",
    "LivenessResult",
    "VoiceLivenessChecker",
]
