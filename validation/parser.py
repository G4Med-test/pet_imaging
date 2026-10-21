#!/usr/bin/env python

# pet_imaging portal parser: metadata() reads the macro, parse() runs the
# bundled GATE analysis script (validation/scripts/analyse_pet.py, already
# uproot-based) against the captured pet.root, then converts each .dat file
# it writes into a scatter or histogram portal record.
#
# Ported from geant-config-generator/tests/geant4/pet_imaging/parser.py
# (gts.BaseParser, single job already — no job-group merge to drop) to the
# module-level metadata()/parse() API expected by
# ci-workflows/validation/export.py. extractObservable()'s .dat parsing is
# unchanged; the subprocess invocation uses subprocess.run with an explicit
# working directory instead of os.system("cd ...; python ...").
#
# NOTE: analyse_pet.py itself imports matplotlib and scipy (for one
# scipy.optimize.curve_fit exponential fit, and a diagnostic PNG this
# parser otherwise ignores) in addition to uproot/numpy — these are not
# mentioned among the packages the geant4-alma9 container ships
# (Python 3.12, NumPy, uproot only, per INTEGRAZIONE_VALIDAZIONE.md), so
# they may need to be added for this parser to actually run in CI.
import os
import subprocess
import sys

from geantval import getJSON, one_command

PARTICLE = "Fluor18"
ENERGY_GEV = 0.512
DETECTOR = "PET"


def metadata(commands):
    # GATE drives acquisition by wall-clock time, not /run/beamOn, so
    # single_run() doesn't apply here.
    one_command(commands, "/gate/application/startDAQ")
    return {"TEST": "pet_imaging",
            "PHYSICS_LIST": one_command(commands, "/gate/physics/addPhysicsList")}


def extract_observable(filename):
    x, y, z, name = [], [], [], []
    with open(filename) as f:
        for line in f:
            if "#" in line:
                label = line.split(":", 1)[1].strip()
                label = label.split(" = ")[0].strip()
                name.append(label)
                continue
            fields = line.split(";")
            x.append(fields[0].strip())
            y.append(fields[1].strip())
            if len(fields) == 3:
                z.append(fields[2].strip())
    return x, y, z, name


def parse(job):
    output_dir = os.path.join(job["path"], "output")
    script_dir = os.path.dirname(os.path.abspath(__file__))
    subprocess.run([sys.executable, os.path.join(script_dir, "analyse_pet.py"), "pet.root"],
                   cwd=output_dir, check=True)

    for filename in sorted(os.listdir(output_dir)):
        if not filename.endswith(".dat"):
            continue
        x, y, z, name = extract_observable(os.path.join(output_dir, filename))
        if len(z) == 0:
            yield getJSON(job, "chart",
                          mctool_name="GEANT4",
                          mctool_model=job["PHYSICS_LIST"],
                          plotType="SCATTER2D",
                          observableName=name[0],
                          targetName=DETECTOR,
                          beamParticle=PARTICLE,
                          beamEnergies=[ENERGY_GEV],
                          title=name[0],
                          secondaryParticle="None",
                          xAxisName=name[1],
                          yAxisName=name[2],
                          xValues=[float(v) for v in x],
                          yValues=[float(v) for v in y])
        else:
            yield getJSON(job, "histogram",
                          mctool_name="GEANT4",
                          mctool_model=job["PHYSICS_LIST"],
                          observableName=name[0],
                          targetName=DETECTOR,
                          beamParticle=PARTICLE,
                          beamEnergies=[ENERGY_GEV],
                          secondaryParticle="None",
                          title=name[0],
                          xAxisName=name[1],
                          yAxisName=name[2],
                          binEdgeLow=[float(v) for v in x],
                          binEdgeHigh=[float(v) for v in y],
                          binContent=[float(v) for v in z])
