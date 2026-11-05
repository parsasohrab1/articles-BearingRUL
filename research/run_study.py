"""NASA IMS bearing run-to-failure data (real test-rig data): health-index alarm and RUL extrapolation.

usage: python research/run_study.py <dir with test1.npz test2.npz test3.npz from extract_features.py>
Failure events (IMS readme): test 1 bearings 3 (inner race) and 4 (roller); test 2 bearing 1 (outer race);
test 3 bearing 3 (outer race). The other 8 bearings did not fail. Only 4 failure events exist: results
are per-event and carry no statistical power.
"""

import json
import sys
from datetime import datetime, timezone
from pathlib import Path

import numpy as np

from bearingrul.health import conformal_threshold, first_alarm, health_index, rul_exponential

FAILING = {(1, 3), (1, 4), (2, 1), (3, 3)}
HEALTHY_FRACTION = 0.4
PERSIST = 5


def hours(names) -> np.ndarray:
    t = np.array(
        [
            datetime.strptime(n, "%Y.%m.%d.%H.%M.%S").replace(tzinfo=timezone.utc).timestamp()
            for n in names
        ]
    )
    return (t - t[0]) / 3600


def persisted(hi, k=PERSIST):
    out = np.full(len(hi), np.nan)
    for i in range(k - 1, len(hi)):
        out[i] = hi[i - k + 1 : i + 1].min()
    return out


def main(folder: str):
    series = []
    for t in (1, 2, 3):
        d = np.load(f"{folder}/test{t}.npz")
        th = hours(d["names"])
        for b in range(d["features"].shape[1]):
            series.append(
                {
                    "test": t,
                    "bearing": b + 1,
                    "t": th,
                    "hi": health_index(d["features"][:, b, :]),
                    "failing": (t, b + 1) in FAILING,
                }
            )
    for s in series:
        n = len(s["hi"])
        s["n_h"] = int(HEALTHY_FRACTION * n)
        s["stat"] = np.nanmax(persisted(s["hi"])[100 : s["n_h"]])
    out = {
        "note": "real IMS run-to-failure data; 12 bearings, 4 failure events; healthy window = first 40 % "
        "of every series; leave-one-series-out threshold calibration (the evaluated failing "
        "series is excluded)",
        "series": [],
        "rules": {},
    }
    for s in series:
        out["series"].append(
            {
                "test": s["test"],
                "bearing": s["bearing"],
                "failing": s["failing"],
                "duration_h": float(s["t"][-1]),
                "max_stat_in_healthy_window": float(s["stat"]),
                "hi_end": float(s["hi"][-1]),
            }
        )
    rules = {
        "conformal_0.1": 0.1,
        "conformal_0.2": 0.2,
        "fixed_5": 5.0,
        "fixed_10": 10.0,
        "fixed_20": 20.0,
    }
    for name, par in rules.items():
        ev = []
        for s in series:
            if not s["failing"]:
                continue
            if name.startswith("conformal"):
                thr = conformal_threshold(np.array([o["stat"] for o in series if o is not s]), par)
            else:
                thr = par
            a = first_alarm(s["hi"], thr, 100, PERSIST)
            ev.append(
                {
                    "test": s["test"],
                    "bearing": s["bearing"],
                    "threshold": thr,
                    "alarm_in_healthy_window": a is not None and a < s["n_h"],
                    "lead_h": None if a is None else float(s["t"][-1] - s["t"][a]),
                    "alarm_at_fraction_of_life": None
                    if a is None
                    else float(s["t"][a] / s["t"][-1]),
                }
            )
        healthy_alarm = []
        for s in series:
            if s["failing"]:
                continue
            thr = (
                conformal_threshold(np.array([o["stat"] for o in series if o is not s]), par)
                if name.startswith("conformal")
                else par
            )
            a = first_alarm(s["hi"], thr, 100, PERSIST)
            healthy_alarm.append(
                {
                    "test": s["test"],
                    "bearing": s["bearing"],
                    "alarm_in_healthy_window": a is not None and a < s["n_h"],
                    "alarm_later": a is not None and a >= s["n_h"],
                }
            )
        out["rules"][name] = {
            "failing_events": ev,
            "non_failing_bearings": {
                "n": len(healthy_alarm),
                "alarm_in_healthy_window": int(
                    sum(h["alarm_in_healthy_window"] for h in healthy_alarm)
                ),
                "alarm_later_in_series": int(sum(h["alarm_later"] for h in healthy_alarm)),
            },
        }
    # RUL extrapolation at fixed times before the end of each failing series (leave-one-event-out fail level)
    rul = []
    fail = [s for s in series if s["failing"]]
    for s in fail:
        level = float(np.median([o["hi"][-1] for o in fail if o is not s]))
        for before in (48, 24, 12, 6):
            i = int(np.argmin(np.abs(s["t"] - (s["t"][-1] - before))))
            w = s["hi"][max(0, i - 60) : i + 1]
            step = float(np.mean(np.diff(s["t"][max(0, i - 60) : i + 1])))
            r = rul_exponential(np.clip(w, 1.0, None), step, level)
            rul.append(
                {
                    "test": s["test"],
                    "bearing": s["bearing"],
                    "true_rul_h": float(s["t"][-1] - s["t"][i]),
                    "pred_rul_h": None if not np.isfinite(r) else r,
                    "fail_level": level,
                }
            )
    out["rul"] = rul
    Path(__file__).with_name("results.json").write_text(json.dumps(out, indent=1))
    for name, v in out["rules"].items():
        print(
            name,
            [
                (
                    e["test"],
                    e["bearing"],
                    round(e["threshold"], 1),
                    e["alarm_in_healthy_window"],
                    None if e["lead_h"] is None else round(e["lead_h"], 1),
                )
                for e in v["failing_events"]
            ],
            v["non_failing_bearings"],
        )
    for r in rul:
        print(
            r["test"], r["bearing"], r["true_rul_h"], r["pred_rul_h"] and round(r["pred_rul_h"], 1)
        )


if __name__ == "__main__":
    main(sys.argv[1])
