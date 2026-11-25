# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Overview

Python astrodynamics library for the Circular Restricted Three-Body Problem (CR3BP) and its extensions (BCR4BP, low-thrust, Sundman-transformed, ephemeris, LVLH). Most of it is built on the ASSET optimal control library (`asset_asrl`).

It is an installable package, `astro_tools`, in a src layout. The Julia port (`Astro.jl`) and the Dash GUI have been removed. `.github/copilot-instructions.md` holds parallel guidance for Copilot, so keep it consistent with this file when conventions change.

## Commands

There are no tests and no CI. Linting and formatting use ruff, configured in `ruff.toml`: line length 120, rule sets `A, D, F, E, I, SIM`, and the numpy docstring convention.

```bash
pip install -e ".[examples,dev]"       # editable install, plus prettytable and ruff
ruff check .            # lint
ruff check . --fix      # lint with autofix
ruff format .           # format
python examples/Solve_NRHOs_CR3BP.py   # works from any CWD; writes to examples/data/Orbits/
```

The example validates the solved NRHOs by printing the computed Jacobi constant and period next to published values. Use it as the end-to-end smoke test for `models/cr3bp.py` and `solvePeriodic`.

## Packaging

- All code lives in `src/astro_tools/`. Subpackages: `models/` (ASSET ODEs), `cr3bp_utils/` (ASSET building blocks), `utils/` (`general`, `plotting`, `pickle_io`, `asset`), and `data/` (package data).
- `pyproject.toml` uses setuptools with `packages.find` under `src/`, so new subpackages are picked up automatically if they have an `__init__.py`. Non-Python files must be listed in `[tool.setuptools.package-data]`. Read package data with `importlib.resources.files("astro_tools")`, not paths relative to the repo.
- The version is single-sourced from `astro_tools.__version__` (`dynamic = ["version"]`).
- prettytable (`examples` extra) and ruff (`dev` extra) are optional dependencies.
- Import with absolute package paths (`from astro_tools.models.cr3bp import CR3BP`). Inside the package, relative imports are fine (`cr3bp_utils/manifolds.py` uses `from ..utils.general import M_TO_KM`). Examples import the installed package and must not modify `sys.path`.
- `astro_tools/__init__.py` holds only `__version__` and must not import submodules, so `import astro_tools` and `astro_tools.astro` work without loading ASSET.

## Architecture

There are two parallel stacks:

1. **`astro_tools.astro` (scipy only, no ASSET).** It defines `CelestialObject` (body data), `characteristicQuantities(P1, P2)` (returns a dict with `mu`, `lstar`, `tstar`, ...), the scipy-format ODEs `cr3bpOde` and `cr3bpOdeStm` (6-state, and 42-state with the flattened STM), `jacobi`, `lagrangePoints`, dim/non-dim conversion, and the differential correctors and continuation routines (`solveLyapunov`, `solveHalo`, `*Continuation`). The correctors integrate with `solve_ivp` and stop on an x-axis crossing event.
2. **ASSET stack (`models/` + `cr3bp_utils/`).** Each file in `models/` defines a Frame class (holds `mu`, `lstar`, `tstar`, `vstar`, computes `P1`/`P2`/`L1`–`L5`) and an ODE class that inherits from `ODEBase` and the Frame. Its `__init__` builds a VectorFunction from `oc.ODEArguments(n_states, n_controls)` and passes it to `ODEBase.__init__`. `cr3bp_utils/` holds functions that take an ASSET `ode` object and return ASSET building blocks (events, constraints, objectives, control laws) or run computations (`solvePeriodic` via phase optimization, `computeStm`/`computeStmParallel`, manifolds and FTLE built on the STM helpers).

`utils/general.py` imports ASSET (constants, `cartesian_to_classic_true`) and holds unit constants (`EARTH_MOON_CR3BP_*`, `M_TO_KM`), KDTree proximity search, and the JPL three-body periodic orbit API client (`queryJpl3BodyApi`, `Jpl3BodyData`). `utils/plotting.py` is Plotly-based. `utils/pickle_io.py` is pickle I/O. `utils/asset.py` wraps ASSET Jet jobs.

### State conventions

- Everything is non-dimensional. P1 is at `[-mu, 0, 0]` and P2 at `[1-mu, 0, 0]`.
- scipy stack: the state is `[x, y, z, vx, vy, vz]`, or 42 elements with the 6×6 STM appended.
- ASSET stack: the state is `[x, y, z, vx, vy, vz, t]`, with time at index 6. Trajectories are lists of these vectors, so `traj[-1][-1]` is the final time. `solvePeriodic`'s `fix_init`/`fix_end` index into this 7-vector, so index 6 is time.
- Sundman-transformed models (`CR3BP_ST`, `EPPR_ST`) change the independent variable. Many `cr3bp_utils/events.py` functions take an `st_flag` to account for this.

## Conventions

- Classes use `UpperCamelCase`. Standalone functions use `camelCase` (`solveHalo`, `computeStmParallel`). Class methods use `snake_case`. Module constants use `UPPER_SNAKE_CASE`. ASSET-derived frame methods keep ASSET's own naming (e.g. `CalcPoints`).
- ASSET aliases at the top of a module: `import asset_asrl as ast`, then `vf = ast.VectorFunctions`, `oc = ast.OptimalControl`, `Args = vf.Arguments`. Some modules import the submodules directly instead.
- Each module starts with a docstring listing its classes and functions, and each subpackage `__init__.py` lists its modules. Update those lists when adding or removing something. Function docstrings use the NumPy style.
- Module and package names are lowercase `snake_case` (`models/cr3bp_st.py`). Class names keep their existing casing (`CR3BP_ST`).
