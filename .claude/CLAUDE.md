# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Overview

Python astrodynamics library for the Circular Restricted Three-Body Problem (CR3BP) and its extensions (BCR4BP, low-thrust, Sundman-transformed, ephemeris, LVLH). Most of it is built on the ASSET optimal control library (`asset_asrl`).

The repo is being turned into an installable package (issue #6). The Julia port (`Astro.jl`) and the Dash GUI have been removed. `.github/copilot-instructions.md` holds parallel guidance for Copilot, so keep it consistent with this file when conventions change.

## Commands

There are no tests and no CI. Linting and formatting use ruff, configured in `ruff.toml`: line length 120, rule sets `A, D, F, E, I, SIM`, and the numpy docstring convention.

```bash
ruff check .            # lint
ruff check . --fix      # lint with autofix
ruff format .           # format
python examples/Solve_NRHOs_CR3BP.py   # run from repo root: it writes to ./data/Orbits/ relative to CWD
```

The example validates the solved NRHOs by printing the computed Jacobi constant and period next to published values. Use it as the end-to-end smoke test for `Models/CR3BP.py` and `solvePeriodic`.

## Packaging state (in flux)

- `pyproject.toml` lists only `asset_asrl` and has no `[build-system]` table. The code also imports numpy, scipy, pandas, matplotlib, plotly and requests, and the example uses prettytable.
- Imports are mixed. Examples add the repo root to `sys.path` and use top-level absolute imports (`from Models.CR3BP import CR3BP`, `from astro import ...`). `CR3BP_Utils/manifolds.py` uses `from ..general_utils import M_TO_KM`, which only resolves if the repo root is imported as a package (the root has an `__init__.py` holding `__version__`). Keep this in mind when changing imports or the layout.
- `Models/` has no `__init__.py`.

## Architecture

There are two parallel stacks:

1. **`astro.py` (scipy only, no ASSET).** It defines `CelestialObject` (body data), `characteristicQuantities(P1, P2)` (returns a dict with `mu`, `lstar`, `tstar`, ...), the scipy-format ODEs `cr3bpOde` and `cr3bpOdeStm` (6-state, and 42-state with the flattened STM), `jacobi`, `lagrangePoints`, dim/non-dim conversion, and the differential correctors and continuation routines (`solveLyapunov`, `solveHalo`, `*Continuation`). The correctors integrate with `solve_ivp` and stop on an x-axis crossing event.
2. **ASSET stack (`Models/` + `CR3BP_Utils/`).** Each file in `Models/` defines a Frame class (holds `mu`, `lstar`, `tstar`, `vstar`, computes `P1`/`P2`/`L1`–`L5`) and an ODE class that inherits from `ODEBase` and the Frame. Its `__init__` builds a VectorFunction from `oc.ODEArguments(n_states, n_controls)` and passes it to `ODEBase.__init__`. `CR3BP_Utils/` holds functions that take an ASSET `ode` object and return ASSET building blocks (events, constraints, objectives, control laws) or run computations (`solvePeriodic` via phase optimization, `computeStm`/`computeStmParallel`, manifolds and FTLE built on the STM helpers).

`general_utils.py` imports ASSET (constants, `cartesian_to_classic_true`) and holds unit constants (`EARTH_MOON_CR3BP_*`, `M_TO_KM`), KDTree proximity search, and the JPL three-body periodic orbit API client (`queryJpl3BodyApi`, `Jpl3BodyData`). `plot_utils.py` is Plotly-based. `data_utils.py` is pickle I/O.

### State conventions

- Everything is non-dimensional. P1 is at `[-mu, 0, 0]` and P2 at `[1-mu, 0, 0]`.
- scipy stack: the state is `[x, y, z, vx, vy, vz]`, or 42 elements with the 6×6 STM appended.
- ASSET stack: the state is `[x, y, z, vx, vy, vz, t]`, with time at index 6. Trajectories are lists of these vectors, so `traj[-1][-1]` is the final time. `solvePeriodic`'s `fix_init`/`fix_end` index into this 7-vector, so index 6 is time.
- Sundman-transformed models (`CR3BP_ST`, `EPPR_ST`) change the independent variable. Many `CR3BP_Utils/events.py` functions take an `st_flag` to account for this.

## Conventions

- Classes use `UpperCamelCase`. Standalone functions use `camelCase` (`solveHalo`, `computeStmParallel`). Class methods use `snake_case`. Module constants use `UPPER_SNAKE_CASE`. ASSET-derived frame methods keep ASSET's own naming (e.g. `CalcPoints`).
- ASSET aliases at the top of a module: `import asset_asrl as ast`, then `vf = ast.VectorFunctions`, `oc = ast.OptimalControl`, `Args = vf.Arguments`. Some modules import the submodules directly instead.
- Each module starts with a docstring listing its classes and functions. Update that list when adding or removing one. Function docstrings use the NumPy style.
