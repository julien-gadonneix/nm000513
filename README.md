[![DOI](https://img.shields.io/badge/DOI-10.82901%2Fnemar.nm000513-blue)](https://doi.org/10.82901/nemar.nm000513)

# Simultaneous EEG-SEEG recordings of deep mesial temporal sources (Mendeley Data 8wz3wvm9y5)

Koessler L, Ternisien E, Cecchin T, Colnat-Coulbois S, Maillard L (Université de Lorraine / CHRU Nancy), Mendeley Data,
doi:10.17632/8wz3wvm9y5, CC BY 4.0. Release description (abridged): nine simultaneous EEG-SEEG datasets corresponding to mesial
temporal networks in seven patients (three females, mean age 38 years) with temporal lobe epilepsy. Within each network the earliest
interictal intracerebral spikes (IIS) with the highest amplitude were marked at the peak of the initial component (t0); EEG and SEEG
segments are 1 s epochs centred on t0, band-pass filtered 1.5-30 Hz, no artifact rejection. Acquisition: 128-channel system, 512 Hz,
analog 0.15 Hz high-pass, scalp FPz reference. Approved by the local ethics committee (CHRU Nancy).

## Content (7 participants, 9 runs, 1945 spike epochs)
- `sub-<p>` = patient P<p>; `acq-net<n>` = mesial network N<n> (patients 1 and 3 have two networks).
- One epoched BrainVision file per network: the bipolar SEEG channels (labels `<shaft><i>_<j>`, typed SEEG) followed by the
  simultaneous scalp EEG channels (release labels prefixed `s`, typed EEG), µV, float32, epochs written back to back
  (`New Segment` marker per epoch); `events.tsv` gives one row per epoch with t0 at 0.5 s.
- Filters: the release states 1.5-30 Hz for EEG and SEEG, but only the scalp EEG channels show the 30 Hz low-pass (more than
  60 dB below the 3-20 Hz level at 35 Hz). The SEEG spectrum falls smoothly with no edge at 30 Hz (about -23 dB at 60 Hz and
  -40 dB at 200 Hz) and has 50 and 150 Hz line-noise peaks in 5 of 9 networks, so the SEEG `high_cutoff` is n/a.
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
