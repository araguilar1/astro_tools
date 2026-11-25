"""
Solve_NRHOs.py

Solve and save the 9:2 and 4:1 L2 Southern NRHOs

Initial Conditions from pages 245-246 of Dr. Emily Spreen's PhD Disseration:
TRAJECTORY DESIGN AND TARGETING FOR APPLICATIONS TO THE EXPLORATION PROGRAM IN CISLUNAR SPACE
"""

from pathlib import Path

import numpy as np
from prettytable import PrettyTable

from astro_tools.astro import CelestialObject, characteristicQuantities, jacobi
from astro_tools.cr3bp_utils.solve_periodic_orbit import solvePeriodic
from astro_tools.models.cr3bp import CR3BP
from astro_tools.utils.general import EARTH_MOON_CR3BP_DAY
from astro_tools.utils.pickle_io import writeDataToPkl

########### Define CR3BP ODE ###########
earth = CelestialObject("Earth")
moon = CelestialObject("Moon")
characteristic_quantities = characteristicQuantities(earth, moon)
mu, lstar, tstar = (
    characteristic_quantities["mu"],
    characteristic_quantities["lstar"],
    characteristic_quantities["tstar"],
)

ode = CR3BP(mu, lstar, tstar)


########### Create Initial Guesses ###########
# 9:2 L2 Southern NRHO
x0_92_L2s_NRHO = np.zeros((7))
x0_92_L2s_NRHO[0] = 1.02134
x0_92_L2s_NRHO[2] = -0.18162
x0_92_L2s_NRHO[4] = -0.10176
x0_92_L2s_NRHO[5] = 9.76561e-07
tf_92_L2s_NRHO = 1.50206

# 4:1 L2 Southern NRHO
x0_41_L2s_NRHO = np.zeros((7))
x0_41_L2s_NRHO[0] = 1.03545
x0_41_L2s_NRHO[2] = -0.19003
x0_41_L2s_NRHO[4] = -0.13071
x0_41_L2s_NRHO[5] = 5.62991e-07
tf_41_L2s_NRHO = 1.68981

########### Solve Each Orbit ###########
traj_92_L2s_NRHO, converged_92_L2s_NRHO = solvePeriodic(x0_92_L2s_NRHO, tf_92_L2s_NRHO, ode, fix_init=[1, 5])
traj_41_L2s_NRHO, converged_41_L2s_NRHO = solvePeriodic(x0_41_L2s_NRHO, tf_41_L2s_NRHO, ode, fix_init=[1, 5])

########### Validate Orbit Period and Jacobi Constant ###########
traj_92_jc = jacobi(traj_92_L2s_NRHO[0], ode.mu)
traj_41_jc = jacobi(traj_41_L2s_NRHO[0], ode.mu)

traj_92_period_days = traj_92_L2s_NRHO[-1][-1] * EARTH_MOON_CR3BP_DAY
traj_41_period_days = traj_41_L2s_NRHO[-1][-1] * EARTH_MOON_CR3BP_DAY

table = PrettyTable()
table.field_names = ["Orbit", "Computed JC", "Disseration JC", "Computed Period", "Disseration Period"]
table.add_row(["9:2 L2 Southern NRHO", traj_92_jc, 3.04719, traj_92_period_days, 6.5556])
table.add_row(["4:1 L2 Southern NRHO", traj_41_jc, 3.03476, traj_41_period_days, 7.375])
print(table)

########### Save Data ###########
output_dir = Path(__file__).parent / "data" / "Orbits"
output_dir.mkdir(parents=True, exist_ok=True)

writeDataToPkl(traj_92_L2s_NRHO, output_dir / "traj_92_L2s_NRHO_CR3BP.pkl")
writeDataToPkl(traj_41_L2s_NRHO, output_dir / "traj_41_L2s_NRHO_CR3BP.pkl")
