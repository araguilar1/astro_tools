# Copilot Instructions

## Overview

Astrodynamics library for the Circular Restricted Three-Body Problem (CR3BP) and related orbital mechanics models. Author: Abram Aguilar.

## Project structure

The code is an installable package, `astro_tools`, in a src layout:

```text
pyproject.toml              # Package metadata, dependencies, setuptools config
ruff.toml                   # Ruff lint and format configuration

src/astro_tools/
  __init__.py               # __version__ only (must not import submodules)
  astro.py                  # scipy-only core: CelestialObject class, CR3BP ODEs, Lagrange points, Jacobi constant,
                            # differential correctors (solveLyapunov, solveHalo), continuation methods
  models/                   # ASSET ODE models
    cr3bp.py                # CR3BP ODE (CR3BPFrame, CR3BP classes)
    bcr4bp.py               # Bicircular Restricted 4-Body Problem (Sun perturbation)
    cr3bp_lt.py             # CR3BP with low-thrust (mass + control variables)
    cr3bp_st.py             # CR3BP with Sundman Transform (regularization near P2)
    eppr_st.py              # Ephemeris Pulsating Rotating frame with Sundman Transform
    lvlh_cr3bp.py           # Local Vertical Local Horizontal frame for RPO
  cr3bp_utils/              # ASSET building blocks and computations
    stm.py                  # State Transition Matrix computation (serial & parallel)
    manifolds.py            # Stable/unstable manifold computation along periodic orbits
    events.py               # ASSET integrator event functions (axis crossings, distance triggers)
    solve_periodic_orbit.py # Generic periodic orbit solver using ASSET phase optimization
    constraints.py          # ASSET equality/inequality constraints (position matching, keep-out zones)
    objectives.py           # ASSET objective functions (delta-V minimization, low-thrust optimal)
    control_laws.py         # VNB-frame thrust direction control laws
    ftle.py                 # Finite-Time Lyapunov Exponent computation
  utils/
    general.py              # Unit conversions, constants (EARTH_MOON_CR3BP_*), KDTree proximity search,
                            # osculating elements, JPL 3-Body API client (Jpl3BodyData)
    plotting.py             # Plotly-based 3D trajectory/Poincare plotting
    pickle_io.py            # Pickle serialization (writeDataToPkl / readDataFromPkl)
    asset.py                # ASSET optimal control solver wrappers (Jet parallel jobs)
  data/
    periodicLagrangeOrbits.csv  # Package data, read via importlib.resources

examples/
  Solve_NRHOs_CR3BP.py      # NRHO solver example
  data/Orbits/              # Pickle output from the example
```

## Dependencies

Python: numpy, scipy, pandas, matplotlib, plotly, requests, asset_asrl. The example scripts also use prettytable.

`pyproject.toml` uses setuptools with `packages.find` under `src/`, so new subpackages with an `__init__.py` are picked up automatically. Non-Python files must be listed in `[tool.setuptools.package-data]`. The version is single-sourced from `astro_tools.__version__`. prettytable is in the `examples` extra and ruff is in the `dev` extra.

The `asset_asrl` package is required by everything in `models/` and `cr3bp_utils/`, by `utils/asset.py`, and by `utils/general.py`. The core `astro_tools.astro` does NOT depend on ASSET (uses scipy directly).

## Running code

Install into any conda or virtual environment from the repository root:

```bash
pip install -e ".[examples,dev]"
```

There is no test suite or CI/CD. Lint and format with ruff (configured in `ruff.toml`: line length 120, rule sets `A, D, F, E, I, SIM`, numpy docstring convention):

```bash
ruff check .
ruff format .
```

Examples import the installed package, so they run from any directory. The NRHO example writes to `examples/data/Orbits/`:

```bash
python examples/Solve_NRHOs_CR3BP.py
```

Import with absolute package paths (e.g., `from astro_tools.models.cr3bp import CR3BP`). Inside the package, relative imports are fine (e.g., `cr3bp_utils/manifolds.py` uses `from ..utils.general import M_TO_KM`). Do not modify `sys.path` in examples. Read package data with `importlib.resources.files("astro_tools")`.

## Naming conventions

- Classes: `UpperCamelCase` (CelestialObject, CR3BPFrame, Jpl3BodyData)
- Class methods: `lower_case_with_underscores` (equatorial_radius, orbit_semi_major_axis)
- Standalone functions: `camelCase` (characteristicQuantities, lagrangePoints, solveHalo)
- Module-level constants: `UPPER_SNAKE_CASE` (EARTH_MOON_CR3BP_MU, M_TO_KM)
- Modules and packages: lowercase `snake_case` (models/cr3bp_st.py); class names keep their existing casing (CR3BP_ST)
- ASSET alias convention at top of files: `vf = ast.VectorFunctions`, `oc = ast.OptimalControl`, `Args = vf.Arguments`

## Key domain concepts

All dynamics use **non-dimensional** coordinates. The CR3BP state vector is `[x, y, z, vx, vy, vz]` (6 elements). ASSET-format states append time as element 7: `[x, y, z, vx, vy, vz, t]`.

- **mu (mass ratio)**: mu = m2 / (m1 + m2), always between 0 and 0.5
- **lstar**: characteristic length (distance between primaries, km)
- **tstar**: characteristic time (seconds), derived as sqrt(lstar^3 / (G * m_star))
- **vstar**: characteristic velocity = lstar / tstar
- **P1**: primary body at [-mu, 0, 0]; **P2**: secondary body at [1-mu, 0, 0]
- **L1-L5**: Lagrange equilibrium points computed by each Frame class
- **STM**: 6x6 State Transition Matrix; when appended to state gives a 42-element vector
- **Jacobi constant**: energy-like integral of motion; computed by `jacobi()` in `astro_tools.astro`
- **Sundman Transform (ST)**: time regularization that scales integration variable by distance to P2

## Docstring style

NumPy-style docstrings with Parameters/Returns sections. Each file starts with a module-level docstring listing all functions and classes, and each subpackage `__init__.py` lists its modules. Follow this pattern when adding new code.

## Common patterns

**Creating a CR3BP system:**

```python
from astro_tools.astro import CelestialObject, characteristicQuantities
from astro_tools.models.cr3bp import CR3BP

earth = CelestialObject("Earth")
moon = CelestialObject("Moon")
cq = characteristicQuantities(earth, moon)
ode = CR3BP(cq["mu"], cq["lstar"], cq["tstar"])
```

**ASSET ODE class pattern** (`models/` subpackage): each model defines a Frame class with equations of motion, then an ODE class that inherits from both `ODEBase` and the Frame class. The `__init__` calls `oc.ODEArguments(n_states, n_controls)`, builds a VectorFunction, and passes it to `ODEBase.__init__`.

**Differential correction**: `solveLyapunov` and `solveHalo` in `astro_tools.astro` use scipy's `solve_ivp` with STM propagation. The ASSET-based `solvePeriodic` in `astro_tools.cr3bp_utils.solve_periodic_orbit` uses ASSET's phase optimization.
