# Software Requirements Specification – BearingRUL

- SR-1 `research/extract_features.py`: per 10-minute snapshot (20 480 samples, 20 kHz) and bearing: RMS, kurtosis, crest factor and high-frequency (>3 kHz) energy share; for test 1 the two channels of a bearing are averaged.
- SR-2 `health.health_index`: mean of the z-scores of log RMS and log kurtosis against the first 100 snapshots of the same bearing, rolling median of 12 snapshots; baseline spread floored at 2 % of the baseline mean.
- SR-3 `health.first_alarm`: first snapshot after the baseline with the index above the threshold for 5 consecutive snapshots.
- SR-4 `health.conformal_threshold`: conformal quantile of the per-series maximum persisted index over the first 40 % of each series; leave-one-series-out (the evaluated failing series is excluded).
- SR-5 `health.rul_exponential`: log-linear extrapolation of the last 60 snapshots to a failure level set as the median end-of-test index of the other three failing series.
- SR-6 Four unit tests on synthetic series (no raw data in the tests).
