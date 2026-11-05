import numpy as np

from bearingrul.health import (
    conformal_threshold,
    first_alarm,
    health_index,
    rolling_median,
    rul_exponential,
)


def _feat(n=300, onset=None, seed=0):
    rng = np.random.default_rng(seed)
    rms = 0.1 * (1 + rng.normal(0, 0.02, n))
    kur = 3 + rng.normal(0, 0.05, n)
    if onset:
        g = np.exp(np.linspace(0, 1.5, n - onset))
        rms[onset:] *= g
        kur[onset:] += (g - 1) * 3
    return np.c_[rms, kur, np.ones(n), np.ones(n)]


def test_healthy_hi_stays_low_and_degraded_hi_rises():
    h = health_index(_feat())
    d = health_index(_feat(onset=150))
    assert np.nanmax(h[100:]) < 6 and d[-1] > 20


def test_alarm_after_onset():
    d = health_index(_feat(onset=150))
    a = first_alarm(d, 8.0, 100)
    assert a is not None and a >= 150


def test_rolling_median_and_threshold():
    assert rolling_median(np.array([1.0, 100.0, 1.0]), 3)[2] == 1.0
    assert conformal_threshold(np.arange(1.0, 100.0), 0.1) == 90.0


def test_rul_exponential_on_clean_trend():
    t = np.arange(50) * 1.0
    hi = 2 * np.exp(0.05 * t)
    r = rul_exponential(hi, 1.0, 2 * np.exp(0.05 * 99))
    assert abs(r - 50) < 1.0
