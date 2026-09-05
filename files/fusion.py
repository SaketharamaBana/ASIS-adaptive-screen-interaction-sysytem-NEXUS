"""Timestamp alignment for commands that combine voice intent and hand position."""

import re
import threading
import time
from collections import deque
from dataclasses import dataclass

import config


_DEICTIC_WORDS = {"this", "here", "that", "there"}
_DEICTIC_PATTERN = re.compile(r"\b(this|here|that|there)\b", re.IGNORECASE)


@dataclass(frozen=True)
class CursorSample:
    """A screen position captured at one point in the gesture stream."""

    timestamp: float
    x: float
    y: float


class CursorHistory:
    """Thread-safe rolling cursor history used by voice and gesture threads."""

    def __init__(self, history_seconds: float = 3.0):
        if history_seconds <= 0:
            raise ValueError("history_seconds must be greater than zero")
        self.history_seconds = history_seconds
        self._samples = deque()
        self._lock = threading.Lock()

    def record(self, x: float, y: float, timestamp: float | None = None):
        """Record a screen position and discard samples outside the time window."""
        sample = CursorSample(time.time() if timestamp is None else timestamp, x, y)
        with self._lock:
            self._samples.append(sample)
            self._discard_old(sample.timestamp)

    def resolve(self, timestamp: float | None = None, max_age: float = 1.5):
        """Return the sample closest to a command timestamp, if it is recent."""
        if max_age < 0:
            raise ValueError("max_age must not be negative")
        target_time = time.time() if timestamp is None else timestamp
        with self._lock:
            self._discard_old(target_time)
            if not self._samples:
                return None
            sample = min(
                self._samples,
                key=lambda candidate: abs(candidate.timestamp - target_time),
            )
        if abs(sample.timestamp - target_time) > max_age:
            return None
        return sample

    def clear(self):
        with self._lock:
            self._samples.clear()

    def _discard_old(self, current_time):
        cutoff = current_time - self.history_seconds
        while self._samples and self._samples[0].timestamp < cutoff:
            self._samples.popleft()


def has_deictic_reference(command: str) -> bool:
    """Return whether a spoken command refers to a gesture-defined location."""
    return bool(_DEICTIC_PATTERN.search(command))


def resolve_deictic_target(command: str, history: CursorHistory, spoken_at=None):
    """Resolve a deictic command to a recent screen point.

    Returns a dictionary suitable for an intent payload, or ``None`` when the
    command has no deictic reference or no sufficiently recent hand position.
    """
    if not has_deictic_reference(command):
        return None
    sample = history.resolve(
        timestamp=spoken_at, max_age=config.FUSION_TARGET_MAX_AGE_SECONDS
    )
    if sample is None:
        return None
    reference = _DEICTIC_PATTERN.search(command).group(1).lower()
    return {
        "reference": reference,
        "x": sample.x,
        "y": sample.y,
        "captured_at": sample.timestamp,
    }


__all__ = [
    "CursorHistory",
    "CursorSample",
    "has_deictic_reference",
    "resolve_deictic_target",
]
