from __future__ import annotations

import numpy as np

FEATURE_ORDER = ("rms", "kurtosis", "crest", "hf_share")


def rolling_median(x: np.ndarray, w: int) -> np.ndarray:
    out = np.empty_like(x, dtype=float)
    for i in range(len(x)):
        out[i] = np.median(x[max(0, i - w + 1) : i + 1])
    return out


def health_index(F: np.ndarray, base: int = 100, smooth: int = 12) -> np.ndarray:
    """F: (n_snapshots, 4) features of one bearing -> HI in baseline standard deviations.

    HI = mean of the z-scores (against the first ``base`` snapshots) of log RMS and log kurtosis,
    smoothed with a rolling median. Baseline spread is floored at 2 % of the baseline mean.
    """
    zs = []
    for j in (0, 1):
        v = np.log(F[:, j])
        b = v[:base]
        sd = max(b.std(), 0.02 * abs(b.mean()), 1e-6)
        zs.append((v - b.mean()) / sd)
    return rolling_median(np.mean(zs, axis=0), smooth)


def first_alarm(hi: np.ndarray, thr: float, start: int, persist: int = 5):
    run = 0
    for t in range(start, len(hi)):
        run = run + 1 if hi[t] > thr else 0
        if run >= persist:
            return t
    return None


def conformal_threshold(max_stats: np.ndarray, alpha: float) -> float:
    n = len(max_stats)
    k = int(np.ceil((n + 1) * (1 - alpha)))
    s = np.sort(max_stats)
    return float(s[k - 1]) if k <= n else float("inf")


def rul_exponential(hi_window: np.ndarray, step_h: float, fail_level: float) -> float:
    """Hours until the log-linear trend of the recent HI window reaches ``fail_level`` (inf if flat)."""
    y = np.log(np.clip(hi_window, 1e-3, None))
    x = np.arange(len(y)) * step_h
    slope, icpt = np.polyfit(x, y, 1)
    if slope <= 1e-9:
        return float("inf")
    return float(max((np.log(fail_level) - (icpt + slope * x[-1])) / slope, 0.0))
