# Portal JSON parser

Rewritten from `geant-config-generator/tests/geant4/pet_imaging/parser.py`
(old `gts.BaseParser`, already single-job) for the module-level
`metadata()`/`parse()` API that `ci-workflows/validation/export.py`
actually calls. `extractObservable()`'s `.dat` parsing is unchanged;
`parse()` still shells out to `analyse_pet.py` (via `subprocess.run` with an
explicit working directory, instead of the original's
`os.system("cd ...; python ...")`), the same as the original — that script
was **already written against `uproot`**, not PyROOT, so nothing needed
porting there, only the calling convention around it.

`metadata()` has no `/run/beamOn` to validate: GATE drives acquisition by
wall-clock simulated time (`/gate/application/setTimeStart`/`setTimeSlice`/
`setTimeStop`/`startDAQ`), not an event count, so `single_run()` (used by
every other parser in this organization) doesn't apply here; `metadata()`
instead just checks `/gate/application/startDAQ` is present.

## The macro: not self-contained in its original form, and why

`geant-config-generator/tests/geant4/pet_imaging/files/mac/main.mac` (and
the copy under `geant-validation-tests/src/Gate/geant-val/pet/mac/`) is a
dispatcher that `/control/execute`s 8 further macros
(`verbose.mac`, `world.mac`, `pet_head.mac`, `pet_digitizer.mac`,
`cylindrical_phantom.mac`, `physics.mac`, `output.mac`, `sources.mac`),
rejected by `read_macro()`. `macro/main.mac` here is that same file with
every `/control/execute` line replaced in-place by the full content of the
file it referenced (each `### inlined from mac/X.mac ###` marker shows the
boundary) — a single flat, self-contained macro with identical behavior,
not a rewrite.

## A dependency this parser needs that others in this organization don't

`analyse_pet.py` imports `matplotlib` and `scipy` (for one
`scipy.optimize.curve_fit` exponential fit and a diagnostic PNG this parser
otherwise ignores), in addition to `uproot`/`numpy`. The geant4-alma9
container this organization's other tests run in is documented (in the
top-level `geant-val/INTEGRAZIONE_VALIDAZIONE.md`) as shipping only
"Python 3.12, NumPy and uproot" — `matplotlib`/`scipy` aren't mentioned, so
they may need to be added to whatever environment actually runs this
parser's `subprocess.run()` call.
