"""
One-Euro Filter for smoothing noisy landmark coordinates in real time.

Adapts smoothing strength to movement speed: heavy smoothing when nearly
still (kills jitter), lighter smoothing when moving fast (kills lag).
Reference: Casiez, Roussel, Vogel (2012).
"""

import math
import time


def _smoothing_factor(t_e: float, cutoff: float) -> float:
    r = 2 * math.pi * cutoff * t_e
    return r / (r + 1)


def _exp_smooth(a: float, x: float, x_prev: float) -> float:
    return a * x + (1 - a) * x_prev


class OneEuroFilter:
    def __init__(self, min_cutoff=1.0, beta=0.0, d_cutoff=1.0):
        self.min_cutoff = min_cutoff
        self.beta = beta
        self.d_cutoff = d_cutoff
        self.x_prev = None
        self.dx_prev = 0.0
        self.t_prev = None

    def filter(self, x: float, t: float = None) -> float:
        if t is None:
            t = time.time()
        if self.x_prev is None:
            self.x_prev, self.dx_prev, self.t_prev = x, 0.0, t
            return x

        t_e = max(t - self.t_prev, 1e-6)
        a_d = _smoothing_factor(t_e, self.d_cutoff)
        dx = (x - self.x_prev) / t_e
        dx_hat = _exp_smooth(a_d, dx, self.dx_prev)

        cutoff = self.min_cutoff + self.beta * abs(dx_hat)
        a = _smoothing_factor(t_e, cutoff)
        x_hat = _exp_smooth(a, x, self.x_prev)

        self.x_prev, self.dx_prev, self.t_prev = x_hat, dx_hat, t
        return x_hat

    def reset(self):
        self.x_prev, self.dx_prev, self.t_prev = None, 0.0, None


class PointOneEuroFilter:
    """Filters an (x, y) point using two independent axis filters."""

    def __init__(self, min_cutoff=1.0, beta=0.0, d_cutoff=1.0):
        self.fx = OneEuroFilter(min_cutoff, beta, d_cutoff)
        self.fy = OneEuroFilter(min_cutoff, beta, d_cutoff)

    def filter(self, x: float, y: float, t: float = None):
        if t is None:
            t = time.time()
        return self.fx.filter(x, t), self.fy.filter(y, t)

    def reset(self):
        self.fx.reset()
        self.fy.reset()
