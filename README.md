# pet_imaging

**In-vivo PET imaging for carbon-ion therapy**: simulates the induced
positron-emitter activity (¹⁸F, ¹⁵O — the latter being the classic
range-verification isotope produced by ¹²C beam fragmentation in tissue)
and its detection by a PET scanner head. Runs on **GATE** (built on Geant4),
not a standalone compiled Geant4 executable.

---

## 🔬 What this test does

A cylindrical phantom containing ¹⁸F and ¹⁵O line sources (`mac/sources.mac`)
is placed inside a PET-head/digitizer geometry (`mac/pet_head.mac`,
`mac/pet_digitizer.mac`); `validation/scripts/analyse_pet.py` reads the
resulting `pet.root` to analyse the reconstructed in-vivo activity.

## ⚠️ Not a standalone Geant4 application

This test is **GATE-macro-driven**: there is no C++ `DetectorConstruction`/
`PhysicsList`/etc. to import, and no `main.cc` to compile. `src/` and
`include/` are left as the empty template placeholders; the actual test
content lives entirely under `macro/` and `validation/`.

Instead of building a Geant4 main, `Apptainer.def` downloads and compiles
**GATE** ([OpenGATE/Gate](https://github.com/OpenGATE/Gate), the C++
macro-driven GATE 9 — not the Python `opengate` 10, which does not read
`.mac` macros) against the Geant4 of the base image, together with ROOT
from EPEL for GATE's listmode output. The GATE release is the `GATE_TAG`
build argument (default `v9.4.2`):

```bash
apptainer build --build-arg GATE_TAG=v9.4.2 pet_imaging.sif Apptainer.def
```

The runscript runs `Gate` on the given macro after creating `output/` and
`data/GateMaterials.db` in the working directory, where the macro expects
them. `macro/unit.mac` (used by the CI unit test) is `macro/main.mac` with
a 2 s acquisition instead of 240 s.

## 📚 Reference

- Source: `geant-validation-tests/src/Gate/geant-val/pet` (inside the
  bundled GATE framework source tree).
- Disclaimer from the original `readme.txt`: *"this is NOT a true PET
  device... designed to check several Gate features... not expected to
  give realistic results."*

## Import notes

- `macro/main.mac` is the entry point (copied from
  `geant-config-generator/tests/geant4/pet_imaging/files/mac/main.mac`,
  with its `%PHYSICS_LIST%` placeholder substituted to `emstandard_opt3`,
  one of the 8 physics lists listed in `params.conf`), then **flattened**:
  its 8 `/control/execute` lines were each replaced in-place with the full
  content of the file they referenced (kept individually, for reference,
  under `macro/mac/`), making it self-contained — see `validation/README.md`
  for why that was necessary.
- `validation/scripts/analyse_pet.py` and `GateMaterials.db` are copied from
  `geant-config-generator/tests/geant4/pet_imaging/files/py/` and
  `files/data/` respectively — the analysis script needed to turn GATE's
  `pet.root` output into the quantities the JSON parser consumes.
- `validation/parser.py` was **rewritten** for the `metadata()`/`parse()`
  module API that `ci-workflows/validation/export.py` actually calls (the
  first version, copied unmodified from
  `geant-config-generator/tests/geant4/pet_imaging/parser.py`, used the old
  `gts.BaseParser` class API and would have failed CI the same way
  `fanoCavity` initially did). See `validation/README.md` for details,
  including a `matplotlib`/`scipy` dependency this test needs that others in
  this organization don't. The vendored `gts` package is no longer needed
  and was removed.
