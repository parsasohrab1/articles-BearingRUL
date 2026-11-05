# articles-BearingRUL

Vibration-based bearing health index, conformal alarm threshold and remaining-useful-life extrapolation on the
**NASA IMS bearing run-to-failure data** (real test-rig data, three tests, four failure events). TRL 4 (public real
laboratory data, laboratory validation only).

```
pip install -e ".[dev]" && python -m pytest
# data: NASA Prognostics Data Repository "IMS Bearing" (not committed); extract each test, then
python research/extract_features.py <test snapshot dir> <1|2|3> <out.npz>
python research/run_study.py <dir with test1.npz test2.npz test3.npz>
```
