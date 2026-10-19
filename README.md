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

The value here is `0.2`, but some examples use `1.0`.  This should
be explored.

Wind is disabled at high temperature via
`max_T_center_for_any_mass_loss` in `inlist_common`.  The timescale of
evolution once the temperature reaches that value is so short that
wind doesn't matter.


### Hydrodynamics

Velocity evolution and the momentum outer boundary condition are
enabled throughout the entire simulation.

### Convection

Convection and semi-convection are enabled (Ledoux convection is
enabled with `alpha_seminconvection = 1`).  The mixing lengths can be
set in `inlist_common`. Overshooting is also enabled.

*Note for comparison*: the `star/test_suite/20M_pre_ms_to_core_collapse` example
uses:

* a custom alpha that is higher in H-rich material and lower elsewhere.
* a much smaller `alpha_semiconvection` of `0.01`.


### Evolution endpoint

The setup evolves from the pre-main sequence toward core collapse,
stopping at `fe_core_infall_limit = 1e8` [cm/s].


##  Space and time controls

The mesh coefficients differ from the defaults in the following ways:

| Control | This setup | Default | Description |
|---|---:|---:|---|
| `mesh_delta_coeff` | 1.0 | 1.0 | Scales mesh-spacing criteria; smaller values produce a finer spatial mesh. |
| `mesh_delta_coeff_for_highT` | 1.0 | 3.0 | Mesh-spacing coefficient used at high central temperatures, with a transition between the standard and high-temperature regimes. |
| `varcontrol_target` | 1e-3 | 1e-3 | Target relative change in stellar structure between models, used to adjust the timestep. |

The timestep limits differ as:

| Control | This setup | Default | Description |
|---|---:|---:|---|
| `time_delta_coeff` | 1.0 | 1.0 | Scales real-valued timestep limits and hard limits; smaller values give finer time resolution. Does not scale `varcontrol_target` or integer iteration limits. |
| `delta_lgT_cntr_limit` | 0.002 | 0.01 | Timestep-control limit on the magnitude of the change in log10 central temperature between models. |
| `delta_lgT_max_limit` | 0.002 | Disabled | Timestep-control limit on the magnitude of the change in log10 of the highest temperature anywhere in the star. |
| `delta_lgRho_cntr_limit` | 0.05 | 0.05 | Timestep-control limit on the magnitude of the change in log10 central density between models. |
| `delta_lgRho_cntr_hard_limit` | 0.1 | Disabled (-1) | Hard limit on the magnitude of the change in log10 central density; exceeding it triggers a retry with a smaller timestep. |
| `delta_lgRho_limit` | 0.1 | 1.0 | Timestep-control limit on the largest magnitude of change in log10 density in any cell. |
| `dX_nuc_drop_limit` | 0.01 | 0.05 | Limits the drop in an isotope's mass fraction from nuclear burning, accounting for replenishment by mixing; larger drops reduce the next timestep. |
| `delta_XSi_cntr_limit` | 0.0025 | 0.01 | Limits the absolute change in central silicon mass fraction between models; larger changes reduce the next timestep. |
| `max_timestep_factor` | 1.05 | 1.2 | Maximum ratio of the next timestep to the previous one, limiting how quickly timesteps can grow. |

Composition resolution is controlled by

| Control | This setup | Default | Description |
|---|---:|---:|---|
| `min_dq_for_xa` | 1e-4 | 1e-14 | Minimum cell size in fractional stellar mass (`dq`) eligible for splitting due to composition gradients where gradr <= grada; larger values suppress refinement of small cells. |
| `min_dq_for_xa_convective` | 1e-6 | 1e-6 | Corresponding minimum cell size for composition-driven splitting where gradr > grada; a nonpositive value uses `min_dq_for_xa` instead. |

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
