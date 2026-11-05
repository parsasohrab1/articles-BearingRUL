"""Turn raw NASA IMS snapshots into per-bearing features (RMS, kurtosis, crest, HF energy share).

usage: python research/extract_features.py <dir with one test's snapshot files> <test 1|2|3> <out.npz>
Raw files are 20 480 samples at 20 kHz, one file per 10 minutes (test 1: 20 minutes at the start).
"""

import sys
from pathlib import Path

import numpy as np
import pandas as pd
from scipy.stats import kurtosis

CH_PER_BEARING = {1: 2, 2: 1, 3: 1}
FS = 20000


def file_features(x: np.ndarray) -> np.ndarray:
    rms = np.sqrt(np.mean(x**2))
    kur = kurtosis(x, fisher=False)
    crest = np.max(np.abs(x)) / rms
    spec = np.abs(np.fft.rfft(x - x.mean())) ** 2
    f = np.fft.rfftfreq(len(x), 1 / FS)
    hf = spec[f > 3000].sum() / spec.sum()
    return np.array([rms, kur, crest, hf])


def main(folder: str, test: int, out: str):
    files = sorted(p for p in Path(folder).iterdir() if p.is_file())
    k = CH_PER_BEARING[test]
    F = []
    for p in files:
        a = pd.read_csv(p, sep="\t", header=None).to_numpy(float)
        F.append(
            [
                np.mean([file_features(a[:, b * k + c]) for c in range(k)], axis=0)
                for b in range(a.shape[1] // k)
            ]
        )
    np.savez(
        out,
        features=np.array(F),
        names=np.array([p.name for p in files]),
        feature_names=np.array(["rms", "kurtosis", "crest", "hf_share"]),
    )
    print(test, np.array(F).shape)


if __name__ == "__main__":
    main(sys.argv[1], int(sys.argv[2]), sys.argv[3])
