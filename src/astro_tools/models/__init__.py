"""
models

ASSET ODE models. Each module defines a Frame class and an ODE class that inherits from ASSET's ODEBase.

Modules
-------
cr3bp      : Circular Restricted Three-Body Problem (CR3BPFrame, CR3BP)
cr3bp_st   : CR3BP with a Sundman transform (CR3BP_ST_FRAME, CR3BP_ST)
cr3bp_lt   : low-thrust CR3BP (CR3BP_LT, CR3BP_LT_ST)
bcr4bp     : Bicircular Restricted Four-Body Problem (BCR4BPFrame, BCR4BP, BCR4BPSB1)
eppr_st    : ephemeris pulsating-rotating frame with a Sundman transform (EPPR_ST_Frame, EPPR_ST)
lvlh_cr3bp : CR3BP relative motion in the LVLH frame (LVLHFrame, LVLHCR3BP)
"""
