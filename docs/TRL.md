# TRL assessment – BearingRUL

**Claimed level: TRL 4** (laboratory validation on public real run-to-failure test-rig data). Not TRL 5: four failure events from one rig, no field operation.

Data: NASA IMS bearings, 12 bearing series (3 tests x 4), 4 failures (test 1 bearings 3 and 4, test 2 bearing 1, test 3 bearing 3); durations of failing series: t1b3 828 h, t1b4 828 h, t2b1 164 h, t3b3 1073 h. Lead = time from first alarm to the end of the test (failure). The healthy window is the first 40 % of each series.

## Alarm results

| Rule | Threshold(s) | Lead per failure event | Non-failing bearings with an alarm: in healthy window / later |
|---|---|---|---|
| conformal_0.1 | 3.4, 2.9, 3.4, 3.4 | t1b3: 273 h; t1b4: 622 h (alarm inside healthy window); t2b1: 55 h; t3b3: 26 h | 0 / 6 of 8 |
| conformal_0.2 | 2.9, 2.8, 2.9, 2.9 | t1b3: 274 h; t1b4: 622 h (alarm inside healthy window); t2b1: 55 h; t3b3: 26 h | 1 / 6 of 8 |
| fixed_5 | 5.0, 5.0, 5.0, 5.0 | t1b3: 81 h; t1b4: 119 h; t2b1: 48 h; t3b3: 25 h | 0 / 4 of 8 |
| fixed_10 | 10.0, 10.0, 10.0, 10.0 | t1b3: 79 h; t1b4: 118 h; t2b1: 45 h; t3b3: 20 h | 0 / 1 of 8 |
| fixed_20 | 20.0, 20.0, 20.0, 20.0 | t1b3: 70 h; t1b4: none; t2b1: 0 h; t3b3: 1 h | 0 / 0 of 8 |

## RUL extrapolation (exponential fit of the last 60 snapshots, leave-one-event-out failure level)

| Event | True RUL | Predicted RUL |
|---|---|---|
| t1b3 | 48 h | 67.5 h |
| t1b3 | 24 h | no estimate (flat trend) |
| t1b3 | 12 h | no estimate (flat trend) |
| t1b3 | 8 h | 6.1 h |
| t1b4 | 48 h | no estimate (flat trend) |
| t1b4 | 24 h | no estimate (flat trend) |
| t1b4 | 12 h | no estimate (flat trend) |
| t1b4 | 8 h | no estimate (flat trend) |
| t2b1 | 48 h | 21.0 h |
| t2b1 | 24 h | 10.8 h |
| t2b1 | 12 h | no estimate (flat trend) |
| t2b1 | 6 h | 17281.4 h |
| t3b3 | 48 h | no estimate (flat trend) |
| t3b3 | 24 h | 6.7 h |
| t3b3 | 12 h | no estimate (flat trend) |
| t3b3 | 6 h | 6.1 h |

## Findings and caveats
- With a fixed threshold of 10 baseline standard deviations the four failures are flagged 20–118 h before the end of the tests, with one alarm in the 8 non-failing bearings. A threshold of 20 is too high (alarm only at the very end or never).
- The conformal threshold (about 3) is much lower than useful: it is calibrated on quiet early-life windows with few series (n = 11) and a bearing's index later drifts well above it, so it alarms early on most bearings, including 6 of the 8 non-failing ones, and it fires inside the healthy window for test 1 bearing 4. Those later alarms on non-failing bearings may be real mechanical coupling to the failing neighbour or a threshold that is too tight; the data cannot tell which.
- **RUL extrapolation does not work reliably here**: it returned no estimate (flat trend) in 9 of 16 cases, and where it did the error is large (e.g. 17 281 h predicted for 6 h left; 21 h for 48 h). Degradation in these tests is abrupt, not a smooth exponential trend, which is the model's assumption.
- Four failure events cannot support any statistical claim; every number above is a case result.
- The failing-bearing labels come from the IMS readme (post-test inspection). The tests were run to failure under constant load and speed, a much cleaner situation than field operation.
