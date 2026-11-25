"""
astro_tools

Astrodynamics tools for the CR3BP and its extensions, for use in trajectory design.

Submodules are not imported here, so ``import astro_tools`` stays light and does not require ASSET.
Import what you need from the submodules directly.

Modules and Subpackages
-----------------------
astro       : scipy-only CR3BP toolkit (bodies, ODEs, Jacobi constant, Lagrange points, differential correctors)
models      : ASSET ODE models (CR3BP, CR3BP_ST, CR3BP_LT, BCR4BP, EPPR_ST, LVLH_CR3BP)
cr3bp_utils : ASSET building blocks (events, constraints, objectives, control laws, STM, manifolds, FTLE,
              periodic orbit solver)
utils       : general utilities, constants, plotting, pickle I/O, and ASSET job helpers
data        : packaged data files (periodicLagrangeOrbits.csv)

Examples
--------
>>> from astro_tools.astro import CelestialObject, characteristicQuantities
>>> from astro_tools.models.cr3bp import CR3BP
"""

__version__ = "0.1.0"
