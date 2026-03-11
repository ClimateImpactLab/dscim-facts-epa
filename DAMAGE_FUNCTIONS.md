# Damage Functions

This document provides detailed documentation for the pre-computed damage function coefficients distributed with DSCIM-FACTS-EPA. These coefficients are the core input for translating climate projections (global mean surface temperature and global mean sea level) into monetized climate damages used to compute the Social Cost of Greenhouse Gases (SC-GHG).

The damage functions were estimated by the Climate Impact Lab (CIL) using the Data-driven Spatial Climate Impact Model (DSCIM). The underlying model computes sector-specific climate damages at roughly 24,000 impact regions worldwide, then aggregates them to the global (or national) level. The coefficients provided here are the result of fitting quadratic regression functions to those globally aggregated damages, year by year, for each of 10,000 probabilistic socioeconomic-climate parameter draws.

For methodological details, see [References](#references).


## Directory structure

After running `directory_setup.py` (or downloading and unzipping the input data), the damage function files are located in `input/damage_functions/`:

```
damage_functions/
|-- damage_function_weights.nc4       # Emulator weights
|-- CAMEL_m1_c0.20/                   # Combined sector, global
|-- CAMEL_m1_c0.20_USA/               # Combined sector, USA
|-- agriculture/                      # Agriculture, global
|-- agriculture_USA/                  # Agriculture, USA
|-- coastal_v0.20/                    # Coastal, global
|-- coastal_v0.20_USA/                # Coastal, USA
|-- energy/                           # Energy, global
|-- energy_USA/                       # Energy, USA
|-- labor/                            # Labor, global
|-- labor_USA/                        # Labor, USA
|-- mortality_v1/                     # Mortality, global
|-- mortality_v1_USA/                 # Mortality, USA
```

Each sector directory contains NetCDF4 files with damage function coefficients for different combinations of valuation recipe and Ramsey discount rate parameters.


## Sectors

| Directory name     | Description |
|--------------------|-------------|
| `agriculture`      | Agricultural productivity damages |
| `coastal_v0.20`    | Coastal damages from sea level rise (version 0.20) |
| `energy`           | Energy expenditure damages (heating and cooling) |
| `labor`            | Labor productivity damages |
| `mortality_v1`     | Mortality damages (version 1) |
| `CAMEL_m1_c0.20`   | **Combined**: all five sectors above, aggregated |

**CAMEL** stands for Coastal, Agriculture, Mortality, Energy, and Labor. The suffix `m1_c0.20` indicates mortality version 1 and coastal version 0.20. Mortality v1 uses VSL (Value of Statistical Life) valuation with ISO-level deaths and impact-region-level costs, and is the EPA main specification. Coastal v0.20 is the original EPA specification using FACTS-based sea level projections (Kopp et al. 2023). CAMEL is the combined multi-sector damage function and is the primary output for computing aggregate SC-GHGs.

There is also an intermediate aggregate, **AMEL** (Agriculture, Mortality, Energy, Labor, i.e. CAMEL without the coastal component), which appears in the codebase configuration but does not have pre-computed coefficient files.

Each sector has a `_USA` variant containing coefficients for damages restricted to the United States, used for computing territorial U.S. SC-GHGs.


## File naming convention

Files follow this pattern:

```
{recipe}_euler_ramsey_eta{eta}_rho{rho}_dfc.nc4
```

Where:

- **recipe**: The valuation approach. Either `risk_aversion` or `adding_up`.
  - `risk_aversion`: Certainty-equivalent damages accounting for risk aversion across climate and socioeconomic uncertainty. This is the primary recipe used in the EPA specification.
  - `adding_up`: A simpler approach that sums damages across regions without certainty-equivalent adjustments. Only available for the CAMEL sector.
- **euler_ramsey**: The discounting framework (Euler equation with Ramsey discounting). All files use this framework.
- **eta**: Elasticity of marginal utility of consumption (the concavity of the CRRA utility function).
- **rho**: Pure rate of time preference.

### Available parameter combinations

| Near-term discount rate | eta     | rho     |
|------------------------|---------|---------|
| 1.5% Ramsey            | 1.016   | 0.0     |
| 2.0% Ramsey            | 1.244   | 0.002   |
| 2.5% Ramsey            | 1.421   | 0.005   |
| 3.0% Ramsey            | 1.568   | 0.008   |

These four (eta, rho) pairs correspond to the near-term certainty-equivalent discount rates described in the EPA technical report. The label (e.g. "2.0% Ramsey") is approximate and used for identification only. The actual discount rate varies over time because it is computed from the realized consumption growth rate of each draw, following stochastic Ramsey discounting (Section 5.1 of the DSCIM User Manual, eq. 11):

```
SDF_ky = product over tau from u to y of exp( -(rho + eta * g_c_k_tau) )
```

where `g_c_k_tau = ln(c_k_tau / c_k_tau-1)` is the consumption growth rate of draw `k` in year `tau`, and `c_k_tau` is global GDP minus climate damages in that draw and year.


## Data structure of coefficient files

Each `.nc4` file is a NetCDF4 dataset with the following structure:

### Dimensions

| Dimension        | Size   | Description |
|-----------------|--------|-------------|
| `discount_type` | 1      | Discounting framework (always `"euler_ramsey"`) |
| `year`          | 281    | Year of the damage function, from 2020 to 2300 |
| `runid`         | 10,000 | RFF socioeconomic pathway draw index (1 to 10,000) |

Each `runid` corresponds to one draw from the joint distribution of socioeconomic projections (from the Resources for the Future Socioeconomic Pathways, RFF-SPv2) and climate model parameters (from FaIR). The mapping between `runid` and underlying scenario parameters is documented in the EPA technical report.

### Variables

The data variables are the **regression coefficients** (betas) of the damage function. Their names correspond to the terms in the regression formula. The variables present depend on the sector:

**Temperature-driven sectors** (agriculture, energy, labor, mortality):

| Variable               | Description |
|------------------------|-------------|
| `anomaly`              | Coefficient on the linear GMST anomaly term |
| `np.power(anomaly, 2)` | Coefficient on the squared GMST anomaly term |

**Coastal sector** (coastal_v0.20):

| Variable               | Description |
|------------------------|-------------|
| `gmsl`                 | Coefficient on the linear GMSL term |
| `np.power(gmsl, 2)`    | Coefficient on the squared GMSL term |

**Combined sector** (CAMEL_m1_c0.20):

| Variable               | Description |
|------------------------|-------------|
| `anomaly`              | Coefficient on the linear GMST anomaly term |
| `np.power(anomaly, 2)` | Coefficient on the squared GMST anomaly term |
| `gmsl`                 | Coefficient on the linear GMSL term |
| `np.power(gmsl, 2)`    | Coefficient on the squared GMSL term |


## Formulas

The damage functions are quadratic regressions (without intercept) of global damages on climate variables. For each sector, year, and SSP-growth model combination, the damage function is estimated by OLS across the 33 GCMs and 2 RCP emissions scenarios (Section 4.2 of the DSCIM User Manual, eq. 4):

```
damages_slpyj = beta1_syj * dGMST_ylp + beta2_syj * dGMST_ylp^2 + error
```

where `l` indexes the climate model, `p` the emissions scenario, `y` the year, `j` the SSP-growth model, and `dGMST` is the temperature anomaly relative to the 2001-2010 average. An analogous equation is estimated for the coastal sector with `dGMSL` in place of `dGMST`. These SSP-based damage functions are then emulated for each of the 10,000 RFF-SP draws (see Appendix B of the User Manual), producing the coefficients stored in these files.

The regression specification for each sector type is:

**Temperature-driven sectors:**
```
damages = beta_anomaly * T + beta_anomaly2 * T^2
```

**Coastal sector:**
```
damages = beta_gmsl * S + beta_gmsl2 * S^2
```

**CAMEL (combined):**
```
damages = beta_anomaly * T + beta_anomaly2 * T^2 + beta_gmsl * S + beta_gmsl2 * S^2
```

Where:
- `T` is the global mean surface temperature (GMST) anomaly
- `S` is global mean sea level (GMSL)
- The beta coefficients are the variables stored in the `.nc4` files

The formulas have no intercept, meaning that zero climate change implies zero damages.


## Units and baselines

### Units of the coefficients

The coefficient files contain no embedded unit metadata. The units are inferred from the DSCIM codebase and preprocessing pipeline:

- The damage function coefficients produce **damages in 2019 PPP-adjusted USD** when multiplied by the climate variables described below. This is confirmed by the DSCIM preprocessing code, which converts underlying RFF-SP GDP data from 2011 USD to 2019 USD using a GDP deflator before estimating the damage functions (see `dscim/utils/rff.py` and `dscim/preprocessing/input_damages.py` in the `dscim` package).
- In the SC-GHG calculation pipeline (`scripts/scghg_utils.py`), the final output is further deflated from 2019 to **2020 USD** using the factor `113.648 / 112.29`. This deflator is applied after the damage functions are evaluated, not within the coefficient files.

The coefficients thus have the following effective units:

| Variable               | Units |
|------------------------|-------|
| `anomaly`              | USD / Celsius |
| `np.power(anomaly, 2)` | USD / Celsius^2 |
| `gmsl`                 | USD / cm |
| `np.power(gmsl, 2)`    | USD / cm^2 |

where USD refers to 2019 PPP-adjusted U.S. dollars, and the resulting damages are in total (global or USA) dollars, not per capita.

### Climate variable baselines

**GMST anomaly (T):** Celsius, relative to the **2001-2010 mean**. The DSCIM pipeline rebases FaIR temperature output (originally relative to 1765) to this base period. The rebasing is done per simulation: for each of the 10,000 draws, the mean temperature over 2001-2010 is subtracted from the full time series. The relevant code is in `Climate.gmst_anomalies` in [`dscim/menu/simple_storage.py` (v0.5.0)](https://github.com/ClimateImpactLab/dscim/blob/v0.5.0/src/dscim/menu/simple_storage.py):

```python
base_period = temps.sel(
    year=slice(self.base_period[0], self.base_period[1])
).mean(dim="year")
anomaly = temps - base_period
```

where `base_period` defaults to `(2001, 2010)`. If you are bringing your own temperature trajectory (for example from DICE), you need to subtract the mean of your control trajectory over 2001-2010 before applying the coefficients.

**GMSL (S):** Centimeters, relative to the **1991-2009 mean**. No rebasing is applied in the pipeline because coastal damages are estimated relative to the same period.

> *Note: FACTS outputs are in millimeters and are converted to centimeters by dividing by 10 before being stored in these files. See `Climate.gmsl_anomalies` in [`simple_storage.py`](https://github.com/ClimateImpactLab/dscim/blob/v0.5.0/src/dscim/menu/simple_storage.py).*

### Spatial aggregation

The coefficients are **globally aggregated** (or USA-aggregated for the `_USA` variants). They do not contain a region dimension. The underlying DSCIM model estimates damages at roughly 24,000 impact regions worldwide, but these coefficients are the result of fitting damage functions to the aggregated output. A researcher using these files works with the relationship between global climate variables and total global damages, not with spatially disaggregated impact estimates.


## Loading the data

The files can be opened with any NetCDF-compatible library. Using Python and xarray:

```python
import xarray as xr

# Load CAMEL risk-aversion coefficients for the 2.0% Ramsey discount rate
ds = xr.open_dataset(
    "input/damage_functions/CAMEL_m1_c0.20/"
    "risk_aversion_euler_ramsey_eta1.244_rho0.002_dfc.nc4"
)

# Access coefficients for a specific year and draw
beta_T = ds["anomaly"].sel(year=2050, runid=1).values       # linear GMST coefficient
beta_T2 = ds["np.power(anomaly, 2)"].sel(year=2050, runid=1).values  # quadratic GMST
beta_S = ds["gmsl"].sel(year=2050, runid=1).values           # linear GMSL coefficient
beta_S2 = ds["np.power(gmsl, 2)"].sel(year=2050, runid=1).values    # quadratic GMSL

# Compute damages given climate inputs
T = 2.0   # GMST anomaly in Celsius relative to 2001-2010
S = 30.0  # GMSL in cm relative to 1991-2009
damages = beta_T * T + beta_T2 * T**2 + beta_S * S + beta_S2 * S**2
# Result is in 2019 PPP-adjusted USD (total global damages)
```


## Using the damage functions in other models

Researchers wishing to integrate these damage functions into DICE or another integrated assessment model should note the following:

1. **Climate variable conventions**: Ensure that your model's temperature and sea level variables use the same baselines (GMST relative to 2001-2010; GMSL relative to 1991-2009) and units (Celsius; centimeters). Rebasing may be required.

2. **Temporal resolution**: Coefficients are provided annually from 2020 to 2300. Each year has its own set of coefficients; the damage function is not time-invariant. This reflects the fact that the relationship between climate variables and damages evolves as the economy grows and adapts.

3. **Probabilistic draws**: The 10,000 `runid` draws represent joint uncertainty in socioeconomic pathways and climate parameters. For a deterministic IAM run, one option is to use the mean (or median) across draws for each year. For uncertainty analysis, the draws can be sampled or used in a Monte Carlo framework.

4. **Sector choice**: For aggregate SC-GHG calculations, use the CAMEL files (combined sector). Individual sector files are useful for understanding the sectoral composition of damages but should not be summed, as the CAMEL coefficients already represent the combined result.

5. **Recipe choice**: The `risk_aversion` recipe is the primary specification used in the EPA analysis. The `adding_up` recipe is a simpler alternative available only for CAMEL. The two recipes differ in how local damages are aggregated. In `adding_up` (risk-neutral), damages across dose-response function draws are averaged within each impact region before summing globally. In `risk_aversion`, a certainty equivalent (CE) is computed within each of the 24,378 impact regions using a CRRA utility function with elasticity eta:

    ```
    CE_cc = [ (1/K) * sum_d( C_d^(1-eta) / (1-eta) ) * (1-eta) ]^(1/(1-eta))
    ```

    where `C_d = GDPpc - damages_d` is per capita consumption in draw `d`. The difference between the CE under no-climate-change and the CE under climate change gives risk-averse damages, which are larger than the risk-neutral mean because they include a premium for severe outcomes. See Section 4.1.2 and Appendix A of the DSCIM User Manual (September 2022) for the full derivation.

6. **Currency conversion**: The coefficients produce damages in 2019 PPP-adjusted USD. Apply a deflator if your model uses a different base year. The DSCIM-FACTS-EPA pipeline uses `113.648 / 112.29` to convert from 2019 to 2020 USD. This deflator is applied after evaluating the damage function, not within the coefficient files.

7. **Marginal damages and SC-GHG**: To compute the SC-GHG, evaluate the damage function under both a control (no-pulse) and pulse climate trajectory, take the difference (marginal damages), discount the stream, and sum. A minimal example:

    ```python
    import xarray as xr

    ds = xr.open_dataset(
        "input/damage_functions/CAMEL_m1_c0.20/"
        "risk_aversion_euler_ramsey_eta1.244_rho0.002_dfc.nc4"
    ).squeeze("discount_type", drop=True)

    def eval_damages(T, S, ds):
        b1 = ds["anomaly"]
        b2 = ds["np.power(anomaly, 2)"]
        b3 = ds["gmsl"]
        b4 = ds["np.power(gmsl, 2)"]
        return b1 * T + b2 * T**2 + b3 * S + b4 * S**2

    # T_control, T_pulse: xr.DataArray with dims (runid, year)
    # S_control, S_pulse: same, in cm relative to 1991-2009
    # T arrays must be rebased to the 2001-2010 mean of the control

    damages_control = eval_damages(T_control, S_control, ds)
    damages_pulse   = eval_damages(T_pulse,   S_pulse,   ds)
    marginal_damages = damages_pulse - damages_control

    # Mean across draws for a deterministic estimate
    marginal_damages_mean = marginal_damages.mean("runid")

    # Convert to 2020 USD
    marginal_damages_2020usd = marginal_damages_mean * (113.648 / 112.29)
    ```

    The gas-specific pulse conversion factors are defined in the run configuration (see `gas_conversions` in the generated config file). The default CO2 pulse conversion is `2.72916487e-10`, which converts a 1 GtC pulse to per-tonne-CO2 units.


## References

- U.S. Environmental Protection Agency (2022). *EPA Report on the Social Cost of Greenhouse Gases: Estimates Incorporating Recent Scientific Advances*. External Review Draft. EPA-HQ-OAR-2021-0317. Available at: https://www.epa.gov/environmental-economics/scghg

- Carleton, T., et al. (2022). Valuing the Global Mortality Consequences of Climate Change Accounting for Adaptation Costs and Benefits. *The Quarterly Journal of Economics*, 137(4), 2037-2105.

- Rode, A., et al. (2021). Estimating a Social Cost of Carbon for Global Energy Consumption. *Nature*, 598, 308-314.

- Rennert, K., et al. (2022). Comprehensive Evidence Implies a Higher Social Cost of CO2. *Nature*, 610, 687-692.

- Resources for the Future (2022). RFF Socioeconomic Projections (RFF-SPv2). https://www.rff.org/publications/data-tools/

- Climate Impact Lab. DSCIM: The Data-driven Spatial Climate Impact Model. https://impactlab.org/

- Smith, C. J., et al. (2018). FAIR v1.3: A simple emissions-based impulse response and carbon cycle model. *Geoscientific Model Development*, 11(6), 2273-2297.

- Kopp, R. E., et al. (2023). The Framework for Assessing Changes To Sea-level (FACTS). *Earth's Future*, 11, e2023EF003790.
