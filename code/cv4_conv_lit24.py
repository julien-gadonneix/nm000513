"""cv4 slice 4: src-literature-24 (Mendeley 8wz3wvm9y5, Koessler/Ternisien, CC BY 4.0) -> BIDS-iEEG. Voyager Job only.
Each folder P<p>_N<n> (patient p, mesial network n) holds SEEG.mat and EEG.mat: cell (1 + n_spikes, n_ch); row 0 = channel labels,
rows 1.. = 1-s epochs (512 samples, 512 Hz) centred on the interictal intracerebral spike peak (t0). One BIDS run per network:
SEEG bipolar channels + simultaneous scalp EEG channels in one epoched BrainVision file."""
import glob, json, os, re, shutil, sys
import numpy as np
import scipy.io as sio
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from o5c_A1_common import write_epochs, events_json, finalize_common, wtsv, wjson, copy_sourcedata, sha256_file

CID = sys.argv[1]
R = os.environ["R"]
SRC = f"{R}/work/open500/src-literature-24"
X = glob.glob(f"{SRC}/_x/*.zip.d/DataBase_BrainTopo")[0]
OUT = f"{R}/work/{CID}/bids"
if os.path.isdir(OUT):
    shutil.rmtree(OUT)
os.makedirs(OUT)
FS = 512.0
report = {"runs": []}
subs = {}
for d in sorted(glob.glob(X + "/P*_N*")):
    tag = os.path.basename(d)
    p, n = re.fullmatch(r"P(\d+)_N(\d+)", tag).groups()
    sub = f"{int(p):02d}"
    subs.setdefault(sub, []).append(tag)
    S = sio.loadmat(d + "/SEEG.mat")["SEEG"]
    E = sio.loadmat(d + "/EEG.mat")["EEG"]
    assert S.shape[0] == E.shape[0]
    sn = [str(np.asarray(x).ravel()[0]) for x in S[0]]
    en = [str(np.asarray(x).ravel()[0]) for x in E[0]]
    rows = list(range(1, S.shape[0]))
    lens = [np.asarray(S[r, 0]).size for r in rows]
    keep = [r for r in rows if lens[r - 1] == 512]
    odd = [r for r in rows if lens[r - 1] != 512]
    oddinfo = []
    for r in odd:
        a = np.asarray(S[r, 0], dtype=float).ravel()
        oddinfo.append({"row": r, "n": int(a.size), "first": a[:5].tolist(), "monotonic": bool(np.all(np.diff(a) > 0))})
    trials = []
    for r in keep:
        s = np.stack([np.asarray(S[r, c], dtype=float).ravel() for c in range(S.shape[1])], axis=1)
        e = np.stack([np.asarray(E[r, c], dtype=float).ravel() for c in range(E.shape[1])], axis=1)
        trials.append(np.concatenate([s, e], axis=1))
    names = sn + en
    types = ["SEEG"] * len(sn) + ["EEG"] * len(en)
    units = ["µV"] * len(names)
    grp = [re.match(r"([A-Za-z']+)", c).group(1) for c in sn] + ["scalp"] * len(en)
    ch_extra = [{"group": g, "reference": ("bipolar" if t == "SEEG" else "FPz"), "low_cutoff": 1.5, "high_cutoff": 30,
                 "description": ("bipolar derivation between adjacent contacts" if t == "SEEG" else "scalp EEG")} for g, t in zip(grp, types)]
    D = f"{OUT}/sub-{sub}/ieeg"
    stem = f"sub-{sub}_task-iis_acq-net{int(n)}"
    sidecar = {"TaskName": "iis", "TaskDescription": "Interictal recording; 1-s epochs centred on the peak of the initial component of an interictal intracerebral spike (IIS) of one mesial temporal network, marked manually (t0)",
               "Manufacturer": "n/a", "PowerLineFrequency": 50, "SoftwareFilters": {"BandPass": {"Description": "1.5-30 Hz band-pass (release description)"}},
               "HardwareFilters": {"HighPass": {"CutoffFrequency": 0.15}}, "iEEGReference": "Recorded against scalp FPz; SEEG channels released as bipolar derivations of adjacent contacts",
               "iEEGGround": "n/a", "iEEGPlacementScheme": "Stereotactic depth electrodes, mesial and lateral temporal lobe (see README)", "ElectricalStimulation": False,
               "RecordingType": "epoched"}
    ev_cols = ["trial_type", "t0_onset"]
    ev_rows = [["IIS", round(0.5, 6)] for _ in keep]
    rep = write_epochs(D, stem, trials, FS, names, units, types, sidecar, ev_cols, ev_rows, ch_extra=ch_extra,
                       comment=f"Mendeley 8wz3wvm9y5 {tag}")
    rep.update({"stem": stem, "source": tag, "n_rows": len(rows), "dropped_rows": oddinfo})
    report["runs"].append(rep)
    print(stem, rep, flush=True)
# events.json
events_json(f"{OUT}/task-iis_events.json", {"trial_type": {"Description": "IIS = interictal intracerebral spike epoch"},
                                            "t0_onset": {"Description": "Time of the spike peak (t0) relative to the start of the epoch; epochs are 1 s centred on t0 (release description)", "Units": "s"}})
# electrodes (contacts from the bipolar labels; no coordinates released)
for sub in subs:
    D = f"{OUT}/sub-{sub}/ieeg"
    contacts = []
    for ch in sorted(glob.glob(D + "/*_channels.tsv")):
        for line in open(ch).read().splitlines()[1:]:
            c, t = line.split("\t")[:2]
            if t != "SEEG":
                continue
            m = re.fullmatch(r"([A-Za-z']+)(\d+)_(\d+)", c)
            for k in (m.group(2), m.group(3)):
                nm = m.group(1) + k
                if nm not in [x[0] for x in contacts]:
                    contacts.append((nm, m.group(1)))
    wtsv(f"{D}/sub-{sub}_space-Other_electrodes.tsv", ["name", "x", "y", "z", "size", "group"], [[a, "n/a", "n/a", "n/a", "n/a", g] for a, g in contacts])
    wjson(f"{D}/sub-{sub}_space-Other_coordsystem.json", {"iEEGCoordinateSystem": "Other", "iEEGCoordinateUnits": "n/a",
          "iEEGCoordinateSystemDescription": "No contact coordinates are released; contacts listed from the bipolar channel labels."})
wtsv(f"{OUT}/participants.tsv", ["participant_id", "age", "sex", "source_id", "networks"], [[f"sub-{s}", "n/a", "n/a", f"P{int(s)}", ",".join(v)] for s, v in sorted(subs.items())])
wjson(f"{OUT}/participants.json", {"age": {"Description": "not given per patient (release: mean age 38 years over the 7 patients)"},
                                   "sex": {"Description": "not given per patient (release: three females)"},
                                   "source_id": {"Description": "patient number in the release folder names (P<p>_N<n>)"},
                                   "networks": {"Description": "release folders (patient_network) of this participant; N<n> -> acq-net<n>"}})
# sourcedata
SD = f"{OUT}/sourcedata/mendeley-8wz3wvm9y5"
files = [(p, os.path.relpath(p, os.path.dirname(X))) for p in sorted(glob.glob(X + "/*/*.mat"))]
files.append((f"{SRC}/files/SEEG electrodes.docx", "SEEG_electrodes.docx"))
copy_sourcedata(files, SD, scrub=True)
os.makedirs(f"{OUT}/code", exist_ok=True)
for f in ("cv4_conv_lit24.py", "o5c_A1_common.py", "b3w10_common.py", "b3w3_common.py"):
    shutil.copy(f"{R}/harness/{f}", f"{OUT}/code/{f}")
wjson(f"{OUT}/code/conversion_report.json", report)
nsp = sum(r["n_trials"] for r in report["runs"])
readme = f"""# Simultaneous EEG-SEEG recordings of deep mesial temporal sources (Mendeley Data 8wz3wvm9y5)

Koessler L, Ternisien E, Cecchin T, Colnat-Coulbois S, Maillard L (Université de Lorraine / CHRU Nancy), Mendeley Data,
doi:10.17632/8wz3wvm9y5, CC BY 4.0. Release description (abridged): nine simultaneous EEG-SEEG datasets corresponding to mesial
temporal networks in seven patients (three females, mean age 38 years) with temporal lobe epilepsy. Within each network the earliest
interictal intracerebral spikes (IIS) with the highest amplitude were marked at the peak of the initial component (t0); EEG and SEEG
segments are 1 s epochs centred on t0, band-pass filtered 1.5-30 Hz, no artifact rejection. Acquisition: 128-channel system, 512 Hz,
analog 0.15 Hz high-pass, scalp FPz reference. Approved by the local ethics committee (CHRU Nancy).

## Content ({len(subs)} participants, {len(report['runs'])} runs, {nsp} spike epochs)
- `sub-<p>` = patient P<p>; `acq-net<n>` = mesial network N<n> (patients 1 and 3 have two networks).
- One epoched BrainVision file per network: the bipolar SEEG channels (labels `<shaft><i>_<j>`, typed SEEG) followed by the
  simultaneous scalp EEG channels (release labels prefixed `s`, typed EEG), µV, float32, epochs written back to back
  (`New Segment` marker per epoch); `events.tsv` gives one row per epoch with t0 at 0.5 s.
- Units: µV, from the release description (amplitudes and thresholds are given in µV); the .mat files do not store units.
- Each release cell array has one extra last row with a different length (775 samples) that is not a 512-sample epoch;
  it is not written to the BIDS runs (kept in sourcedata; see `code/conversion_report.json`, `dropped_rows`).
- No contact coordinates are released: `electrodes.tsv` lists the contacts implied by the bipolar labels with n/a coordinates.
  Shaft -> structure table from the release (`SEEG electrodes.docx`, internal/external structure): P temporal pole/temporal pole,
  A amygdala/superior temporal gyrus, B anterior hippocampus/middle temporal gyrus, C posterior hippocampus/middle temporal gyrus,
  TB entorhinal cortex/inferior temporal gyrus, TM parahippocampal gyrus/middle temporal gyrus, F fusiform gyrus/middle temporal gyrus,
  H insular cortex/Heschl gyrus, T insular cortex/superior temporal gyrus. Shafts with a `b` suffix (Ab, Bb, ...) are not described in the release.
- Age and sex per patient are not released.

## sourcedata/mendeley-8wz3wvm9y5/
Release .mat files and the electrode table; MAT text-header creation day set to 01 (DEIDENTIFICATION_MANIFEST.tsv).

## References
- Koessler L et al. Catching the invisible: mesial temporal source contribution to simultaneous EEG and SEEG recordings. Brain Topogr 2015;28:5-20. doi:10.1007/s10548-014-0417-z
- Ternisien E et al. Extracting the invisible: mesial temporal source detection in simultaneous EEG and SEEG recordings. doi:10.21203/rs.3.rs-2201044/v1
"""
finalize_common(OUT, "Simultaneous EEG-SEEG recordings of deep mesial temporal sources (interictal spike epochs)", "raw", "CC-BY-4.0",
                ["Laurent Koessler", "Eric Ternisien", "Thierry Cecchin", "Sophie Colnat-Coulbois", "Louis Maillard"],
                ["https://doi.org/10.17632/8wz3wvm9y5", "https://doi.org/10.1007/s10548-014-0417-z", "https://doi.org/10.21203/rs.3.rs-2201044/v1"],
                "Cite the Mendeley Data record doi:10.17632/8wz3wvm9y5 and Koessler et al. 2015 (Brain Topogr) / Ternisien et al.",
                ["SEEG", "EEG", "simultaneous EEG-SEEG", "interictal spikes", "temporal lobe epilepsy", "mesial temporal"],
                [{"URL": "https://data.mendeley.com/datasets/8wz3wvm9y5", "DOI": "doi:10.17632/8wz3wvm9y5", "Version": "as downloaded 2026-10-11"}],
                [{"Name": "cv4_conv_lit24.py", "Description": "release cell arrays -> epoched BrainVision; code in code/"}],
                readme, "Converted from Mendeley Data 8wz3wvm9y5 (ieeg-nemar convert_20261014 slice 4).",
                ethics=["Local ethics committee, CHRU Nancy (release description)"])
print("CONVERT_DONE", len(subs), "subjects", nsp, "epochs", flush=True)
