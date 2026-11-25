"""
cr3bp_utils

Functions that take an ASSET ode object and return ASSET building blocks or run computations.

Modules
-------
events               : integrator events (axis crossings, apses, P1/P2 distance)
constraints          : position and distance constraints
objectives           : delta-v, mass, power, and momentum objectives
control_laws         : low-thrust control laws
stm                  : state transition matrix computation and analysis
manifolds            : stable/unstable manifolds of periodic orbits
ftle                 : finite-time Lyapunov exponents
solve_periodic_orbit : periodic orbit solver (solvePeriodic)
"""
