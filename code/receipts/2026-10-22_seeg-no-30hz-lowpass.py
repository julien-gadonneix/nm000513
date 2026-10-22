"""Spectral levels of the SEEG and scalp EEG channels in nm000513, per network.

Usage: python 2026-10-22_seeg-no-30hz-lowpass.py <nm000513 data root> <nm000513 git checkout>
"""

import csv
import hashlib
import subprocess
import sys
from pathlib import Path

import mne
import numpy as np
import scipy
import scipy.signal

EPOCH = 512
BAND = (3, 20)
LINE = (50, 150)
PEAK_DB = 3.0


def sha256(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as f:
        while chunk := f.read(1 << 24):
            h.update(chunk)
    return h.hexdigest()


def git(root: Path, *args: str) -> str:
    out = subprocess.run(["git", "-C", root, *args], capture_output=True, text=True)
    return out.stdout.strip() if out.returncode == 0 else "n/a"


def main(data: Path, checkout: Path) -> None:
    print(f"mne {mne.__version__}, numpy {np.__version__}, scipy {scipy.__version__}")
    print(f"git HEAD of checkout: {git(checkout, 'rev-parse', 'HEAD')}")
    print(
        "\n| run | epochs | eeg sha256 = annex key | SEEG ch | EEG ch | SEEG high_cutoff "
        "in channels.tsv | EEG median dB @35 Hz (least attenuated ch) | SEEG median dB "
        "@30 / 35 / 60 / 200 Hz | SEEG mean-spectrum peak dB @50 / 150 Hz | line noise |"
    )
    print("|---|---:|---|---:|---:|---|---|---|---|---|")
    seeg_db, n_line, f = [], 0, None
    for vhdr in sorted(data.glob("sub-*/ieeg/*_ieeg.vhdr")):
        rel = vhdr.relative_to(data).with_suffix(".eeg").as_posix()
        key = git(checkout, "cat-file", "-p", f"HEAD:{rel}").rsplit("--", 1)[-1]
        same = key.startswith(sha256(data / rel))
        tsv = checkout / rel.replace("_ieeg.eeg", "_channels.tsv")
        with tsv.open(encoding="utf-8") as fh:
            chans = list(csv.DictReader(fh, delimiter="\t"))
        raw = mne.io.read_raw_brainvision(vhdr, preload=True, verbose="error")
        assert raw.ch_names == [c["name"] for c in chans], f"{tsv.name}: channel order"
        assert raw.n_times % EPOCH == 0, f"{vhdr.name}: {raw.n_times} samples"
        x = raw.get_data(units="uV")
        epochs = x.reshape(len(chans), -1, EPOCH)
        f, p = scipy.signal.periodogram(epochs, fs=raw.info["sfreq"], window="hann")
        p = p.mean(axis=1)
        db = 10 * np.log10(p)
        db -= db[:, (f >= BAND[0]) & (f <= BAND[1])].mean(axis=1, keepdims=True)
        types = np.array([c["type"] for c in chans])
        seeg, eeg = types == "SEEG", types == "EEG"
        seeg_db.append(db[seeg])
        mean_db = 10 * np.log10(p[seeg].mean(axis=0))
        peaks = []
        for fr in LINE:
            side = ((f >= fr - 5) & (f <= fr - 2)) | ((f >= fr + 2) & (f <= fr + 5))
            peaks.append(mean_db[f == fr][0] - mean_db[side].mean())
        line = all(pk > PEAK_DB for pk in peaks)
        n_line += line
        at = {fr: np.median(db[seeg][:, f == fr]) for fr in (30, 35, 60, 200)}
        e35 = db[eeg][:, f == 35][:, 0]
        cutoffs = sorted({c["high_cutoff"] for c in chans if c["type"] == "SEEG"})
        print(
            f"| {vhdr.name.split('_acq-')[1][:4]} | {epochs.shape[1]} | {same} | "
            f"{seeg.sum()} | {eeg.sum()} | {', '.join(cutoffs)} | {np.median(e35):.1f} "
            f"({e35.max():.1f}) | {' / '.join(f'{v:.1f}' for v in at.values())} | "
            f"{peaks[0]:.1f} / {peaks[1]:.1f} | {'yes' if line else 'no'} |"
        )
    pooled = np.concatenate(seeg_db)
    levels = ", ".join(
        f"{fr} Hz {np.median(pooled[:, f == fr]):.1f} dB" for fr in (30, 60, 200)
    )
    print(f"\nall {len(pooled)} SEEG channels, median: {levels}")
    print(f"networks with line-noise peaks at 50 and 150 Hz: {n_line}")


if __name__ == "__main__":
    main(Path(sys.argv[1]), Path(sys.argv[2]))
