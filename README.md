# MESA massive star setup

This is a MESA massive star setup based on the lab from Ebraheem Farag at:
https://debraheem.github.io/astronuc/


## Basic parameters

### Mass and metalicity

This setup will evolve from the pre-main sequence to generate
an initial model.  The mass and metalicity of the initial star
are set in `inlist_mass_Z_wind_rotation`.


## Network

The network can be set in `inlist_project` as `new_net_name`.  The
`approx21_plus_co56.net` runs very well with this setup.


### Wind

Dutch wind is used, with the factor controlling the wind specified
in `inlist_mass_Z_wind_rotation` as `Dutch_scaling_factor`.  It
can be turned off by setting this to 0.

Wind is disabled at high temperature via
`max_T_center_for_any_mass_loss` in `inlist_common`.  The timescale of
evolution once the temperature reaches that value is so short that
wind doesn't matter.


### Hydrodynamics

Velocity evolution and the momentum outer boundary condition are
enabled throughout the entire simulation.

### Convection

Convection and semi-convection are enabled (Ledoux convection is
enabled with `alpha_seminconvection = 1`.  The mixing lengths can be
set in `inlist_common`. Overshooting is also enabled.


### Evolution endpoint

The setup evolves from the pre-main sequence toward core collapse,
stopping at `fe_core_infall_limit = 1e8` [cm/s].


##  Space and time controls

The mesh coefficients differ from the defaults in the following ways:

| Control | This setup | Default | Effect |
|---|---:|---:|---|
| `mesh_delta_coeff` | 2.0 | 1.0 | Coarser mesh during most of the evolution |
| `mesh_delta_coeff_for_highT` | 1.5 | 3.0 | Finer mesh at high central temperature |
| `varcontrol_target` | 1e-3 | 1e-3 | Unchanged |

The timestep limits differ as:

| Control | This setup | Default | Effect |
|---|---:|---:|---|
| `time_delta_coeff` | 1.0 | 1.0 | Unchanged overall timestep multiplier |
| `delta_lgT_cntr_limit` | 0.002 | 0.01 | 5× tighter central-temperature change limit |
| `delta_lgT_max_limit` | 0.002 | Disabled | Adds a maximum-temperature change limit |
| `delta_lgRho_cntr_limit` | 0.05 | 0.05 | Unchanged |
| `delta_lgRho_limit` | 0.1 | 1.0 | 10× tighter density-change limit |
| `dX_nuc_drop_limit` | 0.01 | 0.05 | 5× tighter abundance-drop limit |
| `delta_XSi_cntr_limit` | 0.0025 | 0.01 | 4× tighter central silicon-change limit |
| `max_timestep_factor` | 1.05 | 1.2 | Slower permitted timestep growth |

Composition resolution is controlled by

| Control | This setup | Default | Effect |
|---|---:|---:|---|
| `min_dq_for_xa` | 1e-4 | 1e-14 | Restricts composition-driven refinement where gradr <= grada |
| `min_dq_for_xa_convective` | 1e-6 | 1e-6 | Unchanged composition-driven refinement threshold where gradr > grada |

The control for non-convective regions is much looser.

## Tolerances and solver

### Central fuel depletion

Central fuel depletion controls are set via `inlist_project`
as `delta_lg_X{H,He,C,O}_cntr_min = 0.5`, which is a log control,
so this effectively disables them.

### Abundance checks

The high temperature limits for abundances are disabled in `inlist_common`
(see `min_xa_hard_limit_for_highT` and `sum_xa_hard_limit_for_highT`).

### Energy-error limits

The limit on relative energy-conservation error timestep changes is disabled in `inlist_common`
(see `limit_for_rel_error_in_energy_conservation`).

### Residual tolerances

`run_star_extras.f90` loosens the tolerances on burning convergence at
late times (high temperatures).




### Operator-splitting

Operator-splitting of the burning is off by default.  It can be
enabled by setting `op_split_burn = .true.` in `inlist_common`.  There
is also a control to determine at what temperature it kicks in.

This may be needed for large networks.
