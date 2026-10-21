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
content lives entirely under `macro/` and `validation/`. Running it requires
a GATE installation (built on top of Geant4), not just `cmake --build`.

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
