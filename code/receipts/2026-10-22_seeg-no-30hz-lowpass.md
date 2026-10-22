# Receipt: SEEG channels show no 30 Hz low-pass: high_cutoff n/a (v1.0.3)

**Claim**: the release's 1.5-30 Hz band-pass shows in the scalp EEG channels only. The 739 SEEG channels have no 30 Hz edge, so their `high_cutoff` is n/a (was 30).

**PR**: nemarDatasets/nm000513#3, receipt on top of head `2bc09704`.

## Source
- NEMAR nm000513 `origin/main` `cad0c8b994d71661533d8d432aada0e3e52dad01`: all 9 `sub-*/ieeg/*_ieeg.{vhdr,eeg}` runs, with `channels.tsv` read from that commit. Each `.eeg` sha256 equals its git-annex key at that commit (column "sha256 = annex key"). The PR changes no data file.
- Filter statement: Mendeley Data doi:10.17632/8wz3wvm9y5, version 2 (published 2022-12-20), dataset description: "EEG-SEEG segments were extracted using the same 1 sec epoch centered on t0 as SEEG segments. The remaining segments were band-pass filtered (1.5-30 Hz)."

## Method
- Reader: MNE 1.13.2 `read_raw_brainvision`, `get_data(units="uV")`, i.e. the stored float32 values (resolution 1, unit µV). Channel type (SEEG / EEG) comes from `channels.tsv`.
- Each run is cut into its 512-sample epochs (1 s at 512 Hz, written back to back). For each epoch: scipy 1.18.1 `periodogram` with a Hann window (1 Hz bins). Power is averaged over epochs.
- Per channel: dB relative to that channel's 3-20 Hz level (the mean of its dB values over 3-20 Hz).
- Levels: the median over the run's channels of each type, at 30/35/60/200 Hz. The least attenuated EEG channel at 35 Hz is given in brackets.
- Line noise: in the run's mean SEEG power spectrum, the 50 Hz and 150 Hz bins are compared with the mean of the bins 2-5 Hz on either side. A run is flagged when both exceed it by more than 3 dB.

## Result
| run | epochs | eeg sha256 = annex key | SEEG ch | EEG ch | SEEG high_cutoff in channels.tsv | EEG median dB @35 Hz (least attenuated ch) | SEEG median dB @30 / 35 / 60 / 200 Hz | SEEG mean-spectrum peak dB @50 / 150 Hz | line noise |
|---|---:|---|---:|---:|---|---|---|---|---|
| net1 | 273 | True | 78 | 8 | 30 | -60.9 (-58.1) | -12.9 / -15.1 / -23.2 / -36.8 | -0.2 / 0.2 | no |
| net2 | 149 | True | 78 | 8 | 30 | -63.3 (-61.3) | -13.1 / -15.5 / -23.9 / -37.1 | -0.1 / 0.2 | no |
| net3 | 439 | True | 71 | 25 | 30 | -65.2 (-57.1) | -12.9 / -15.3 / -22.9 / -36.4 | 25.8 / 24.2 | yes |
| net4 | 170 | True | 89 | 13 | 30 | -71.5 (-62.3) | -14.2 / -16.4 / -23.4 / -40.6 | 17.7 / 17.5 | yes |
| net5 | 93 | True | 89 | 13 | 30 | -67.9 (-66.1) | -14.9 / -16.6 / -24.6 / -40.7 | 19.5 / 19.7 | yes |
| net6 | 160 | True | 75 | 13 | 30 | -63.5 (-57.4) | -12.9 / -15.2 / -23.8 / -40.1 | -0.1 / 0.2 | no |
| net7 | 367 | True | 100 | 14 | 30 | -63.3 (-60.0) | -14.3 / -16.9 / -25.0 / -40.1 | 0.3 / 2.5 | no |
| net8 | 247 | True | 102 | 12 | 30 | -69.1 (-66.9) | -12.2 / -14.3 / -20.4 / -35.2 | 12.5 / 17.1 | yes |
| net9 | 47 | True | 57 | 20 | 30 | -64.9 (-46.2) | -12.6 / -14.7 / -21.8 / -34.9 | 8.2 / 14.9 | yes |

- Scalp EEG: in every run, the median EEG channel is more than 60 dB below its 3-20 Hz level at 35 Hz (-60.9 to -71.5 dB).
- SEEG, at the same 35 Hz: -14.3 to -16.9 dB.
- All 739 SEEG channels, median: 30 Hz -13.3 dB, 60 Hz -23.2 dB, 200 Hz -38.4 dB (per run, 200 Hz ranges from -34.9 to -40.7 dB). This is the "about -23 dB at 60 Hz and -40 dB at 200 Hz" in the README and ieeg.json.
- Line-noise peaks at 50 and 150 Hz: 5 of 9 networks (net3, net4, net5, net8, net9). Flagged runs reach at least 8.2 dB at 50 Hz, the others at most 0.3 dB.
- Rows changed by the PR: the 739 SEEG rows (high_cutoff 30 -> n/a) of the 9 channels.tsv files. The 126 EEG rows are unchanged (checked with `git diff` against `origin/main`).

## Coverage
9 of 9 runs (1945 epochs), all 739 SEEG and 126 EEG channels.

## Reproduce
```
uv run --no-project --python 3.12 --with mne==1.13.2 --with scipy python code/receipts/2026-10-22_seeg-no-30hz-lowpass.py <nm000513 data root> <nm000513 git checkout>
```
Run on 2026-10-22 (Slurm job 13448585). The data root was a NEMAR download of `origin/main`. The checkout, used for the annex keys and `channels.tsv`, was `origin/main` `cad0c8b`.
