# Damage Functions

This document provides detailed documentation for the pre-computed damage function coefficients distributed with DSCIM-FACTS-EPA. These coefficients are the core input for translating climate projections (global mean surface temperature and global mean sea level) into monetized climate damages used to compute the Social Cost of Greenhouse Gases (SC-GHG).

The damage functions were estimated by the Climate Impact Lab (CIL) using the Data-driven Spatial Climate Impact Model (DSCIM). The underlying model computes sector-specific climate damages at roughly 24,000 impact regions worldwide, then aggregates them to the global (or national) level. The coefficients provided here are the result of fitting quadratic regression functions to those aggregated damages, year by year for each socioeconomics pathway**. (**Note, damage functions are initially estimated on damages based on Shared Socioeconomic Pathways, or SSPs. Those damage functions are then used to emulate damage functions for Resources for the Future Socioeconomic Pathways, or RFF-SPs, provided here).

For methodological details, see [References](#references).


## Directory structure

After running `directory_setup.py` (or downloading and unzipping the input data), the damage function files are located in `input/damage_functions/`:

```
damage_functions/
|-- damage_function_weights.nc4       # Emulator weights
|-- CAMEL_m1_c0.20/                   # Combined sectors, global
|-- CAMEL_m1_c0.20_USA/               # Combined sectors, USA
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

Each sector directory contains NetCDF4 files with damage function coefficients for different combinations of valuation recipe and `eta` (elasticity of marginal utility of consumption) parameters.


## Sectors

| Directory name     | Description |
|--------------------|-------------|
| `agriculture`      | Agricultural productivity damages |
| `coastal_v0.20`    | Coastal damages from sea level rise (version 0.20) |
| `energy`           | Energy expenditure damages (heating and cooling) |
| `labor`            | Labor productivity damages |
| `mortality_v1`     | Mortality damages (version 1) |
| `CAMEL_m1_c0.20`   | **Combined**: all five sectors above, aggregated |

**CAMEL** stands for Coastal, Agriculture, Mortality, Energy, and Labor. The suffix `m1_c0.20` indicates mortality version 1 and coastal version 0.20. Mortality v1 uses VSL (Value of Statistical Life) valuation with ISO-level VSL applied to deaths and impact-region-level VSL applied to adaptation costs, and is the EPA main specification. Coastal v0.20 is the original EPA specification using FACTS-based sea level projections (Kopp et al. 2023). CAMEL is the combined multi-sector damage function and is the primary output for computing aggregate SC-GHGs.

Each sector has a `_USA` variant containing coefficients for damages restricted to the United States, used for computing territorial U.S. SC-GHGs.

## File naming convention

> Note: the damage function coefficient filenames have many quirks that can be confusing, so we aim to be transparent about those here. The quirks are a function of the way settings are handled and filenames are set up in the `dscim` library. We are planning to improve output names among other things in a future release.

Files follow this pattern:

```
{recipe}_euler_ramsey_eta{eta}_rho{rho}_dfc.nc4
```

Where:

- **recipe**: The valuation approach. Either `risk_aversion` or `adding_up`.
  - `risk_aversion`: Indicates the damage functions were fit on certainty-equivalent damages accounting for uncertainty in the underlying statistical relationships between impact region damages and weather. This is the primary recipe used in the EPA specification.
  - `adding_up`: Indicates the damage functions were fit on mean, not certainty equivalent, damages. This is also known as "risk neutral". Only available for the CAMEL sector.
- **euler_ramsey**: Discount method. **This can be ignored** - damage functions do not vary by discount type. 
- **eta**: Elasticity of marginal utility of consumption (the concavity of the CRRA utility function) used in the certainty-equivalent calculation. This setting is **only applicable to `risk_aversion` damage functions**. Although there exists an `adding_up` file for each `eta` in the directory, they are exactly the same.
- **rho**: Pure rate of time preference. **This can be ignored** - damage functions do not vary by `rho`. 

## Data structure of coefficient files

Each `.nc4` file is a NetCDF4 dataset with the following structure:

### Dimensions

| Dimension        | Size   | Description |
|-----------------|--------|-------------|
| `discount_type` | 1      | Discounting framework (always `"euler_ramsey"`) **Should be ignored** |
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

The damage functions are quadratic regressions (without intercept) of global damages on climate variables. For each sector, year, and SSP-growth model combination, the damage function is estimated by ordinary least-squares regression across the 33 GCMs and 2 RCP emissions scenarios (Section 4.2 of the DSCIM User Manual). These SSP-based damage functions are then used to emulate damage functions for each of the 10,000 RFF-SP draws (see Appendix B of the User Manual), producing the coefficients stored in these files.

The regression specification for each sector type is:

**Temperature-driven sectors:**
```
damages = beta_gmst * T + beta_gmst2 * T^2
```

**Coastal sector:**
```
damages = beta_gmsl * S + beta_gmsl2 * S^2
```

**CAMEL (combined):**
```
damages = beta_gmst * T + beta_gmst2 * T^2 + beta_gmsl * S + beta_gmsl2 * S^2
```

Where:
- `T` is the global mean surface temperature (GMST) anomaly
- `S` is global mean sea level (GMSL) anomaly
- The beta coefficients are the variables stored in the `.nc4` files

The formulas have no intercept, meaning that zero climate change implies zero damages.


## Units and baselines

### Units of the coefficients

The coefficient files contain no embedded unit metadata. The units are inferred from the DSCIM codebase and preprocessing pipeline:

- The damage function coefficients produce **damages in 2019 PPP-adjusted USD** when multiplied by the climate variables described below. 
- The final SC-GHG output is converted from 2019 to **2020 USD** using the factor `113.648 / 112.29`. This deflator is applied after the damage functions are evaluated, not within the coefficient files.

The coefficients thus have the following effective units:

| Variable               | Units |
|------------------------|-------|
| `anomaly`              | USD / Celsius |
| `np.power(anomaly, 2)` | USD / Celsius^2 |
| `gmsl`                 | USD / cm |
| `np.power(gmsl, 2)`    | USD / cm^2 |

where USD refers to 2019 PPP-adjusted U.S. dollars, and the resulting damages are in total (global or USA) dollars, not per capita.

### Required climate variable baselines

**GMST anomaly (T):** Celsius, relative to the **2001-2010 mean**. The DSCIM pipeline rebases FaIR temperature output to this base period. If you are bringing your own temperature trajectory, you need to subtract the mean of the trajectory over 2001-2010 before applying the coefficients.

**GMSL (S):** Centimeters, relative to the **1991-2009 mean**. No rebasing is applied in the pipeline because coastal damages are estimated relative to the same period. If you are bringing your own sea level trajectory, you need to subtract the mean of the trajectory over 1991-2009 before applying the coefficients.

> *Note: FACTS outputs are in millimeters and are converted to centimeters by dividing by 10 before being stored in these files.*

## Loading and applying the coefficients

The files can be opened with any NetCDF-compatible library. Using Python and xarray:

```python
import xarray as xr

# Load CAMEL risk-aversion coefficients for the 2.0% Ramsey discount rate
ds = xr.open_dataset(
    "input/damage_functions/CAMEL_m1_c0.20/"
    "risk_aversion_euler_ramsey_eta1.244_rho0.002_dfc.nc4"
)

# Access coefficients for a specific year and draw
beta_gmst = ds["anomaly"].sel(year=2050, runid=1).values       # linear GMST coefficient
beta_gmst2 = ds["np.power(anomaly, 2)"].sel(year=2050, runid=1).values  # quadratic GMST
beta_gmsl = ds["gmsl"].sel(year=2050, runid=1).values           # linear GMSL coefficient
beta_gmsl2 = ds["np.power(gmsl, 2)"].sel(year=2050, runid=1).values    # quadratic GMSL

# Compute damages given climate inputs
T = 2.0   # GMST anomaly in Celsius relative to 2001-2010
S = 30.0  # GMSL in cm relative to 1991-2009
damages = beta_gmst * T + beta_gmst2 * T**2 + beta_gmsl * S + beta_gmsl2 * S**2
# Result is in 2019 PPP-adjusted USD (total global damages)
```


## Using the damage functions

Researchers wishing to use these damage functions should note the following:

1. **Climate variable conventions**: Ensure that your model's temperature and sea level variables use the same baselines (GMST relative to 2001-2010; GMSL relative to 1991-2009) and units (Celsius; centimeters).

2. **Temporal resolution**: Coefficients are provided annually from 2020 to 2300. Each year has its own set of coefficients; the damage function is not time-invariant. This reflects the fact that the relationship between climate variables and damages evolves as the economy grows and adapts.

3. **Probabilistic draws**: Coefficients are provided for each of 10,000 `runid` draws, which represent joint uncertainty in socioeconomic pathways and climate parameters. 

4. **Sector choice**: For aggregate SC-GHG calculations, use the CAMEL files ("combined" sector). Individual sector files are useful for understanding the sectoral composition of damages but should not be summed, as the CAMEL coefficients already represent the combined result.

5. **Recipe choice**: The `risk_aversion` recipe is the primary specification used in the EPA specification. The `adding_up` recipe is a "risk neutral" alternative available only for CAMEL. The two recipes differ in how local damages are aggregated. In `adding_up` (risk-neutral), damages across dose-response function draws are averaged within each impact region before summing globally and fitting the damage function. In `risk_aversion`, a certainty equivalent (CE) is computed within each of the 24,378 impact regions using a CRRA utility function with elasticity `eta`, before summing globally and fitting the damage function. Risk-averse damages are typically larger than the risk-neutral mean because they include a premium for severe outcomes. See Section 4.1.2 and Appendix A of the DSCIM User Manual (September 2023) for the full derivation.

6. **Currency units**: The coefficients produce damages in 2019 PPP-adjusted USD. The DSCIM-FACTS-EPA pipeline uses `113.648 / 112.29` to convert the calculated SC-GHGs from 2019 to 2020 USD.

## References

- U.S. Environmental Protection Agency (2022). *EPA Report on the Social Cost of Greenhouse Gases: Estimates Incorporating Recent Scientific Advances*. External Review Draft. EPA-HQ-OAR-2021-0317. Available at: https://www.epa.gov/environmental-economics/scghg

- Carleton, T., et al. (2022). Valuing the Global Mortality Consequences of Climate Change Accounting for Adaptation Costs and Benefits. *The Quarterly Journal of Economics*, 137(4), 2037-2105.

- Rode, A., et al. (2021). Estimating a Social Cost of Carbon for Global Energy Consumption. *Nature*, 598, 308-314.

- Rennert, K., et al. (2022). Comprehensive Evidence Implies a Higher Social Cost of CO2. *Nature*, 610, 687-692.

- Resources for the Future (2022). RFF Socioeconomic Projections (RFF-SPv2). https://www.rff.org/publications/data-tools/

- Climate Impact Lab. DSCIM: The Data-driven Spatial Climate Impact Model. https://impactlab.org/research/data-driven-spatial-climate-impact-model-user-manual-version-092023-epa/

- Smith, C. J., et al. (2018). FAIR v1.3: A simple emissions-based impulse response and carbon cycle model. *Geoscientific Model Development*, 11(6), 2273-2297.

- Kopp, R. E., et al. (2023). The Framework for Assessing Changes To Sea-level (FACTS). *Earth's Future*, 11, e2023EF003790.
