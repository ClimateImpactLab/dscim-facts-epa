import os
import sys
import xarray as xr
import pandas as pd
import numpy as np
import argparse
import pickle
from datetime import datetime
from itertools import product
from pathlib import Path
import shutil
from datatree import DataTree

scenario = 'ssp585'
nsamps = 10000
proj_years = np.arange(1750, 2501)


pulse_years = ['control', 2020]
gases = ['CO2_Fossil']

for pulse_year, gas in product(pulse_years,gases):
    template_dir = Path(os.getcwd()) / 'template'
    run_dir = Path(os.getcwd()) / f'rff.{pulse_year}.{gas}'
    input_dir = run_dir / "input"
    os.makedirs(run_dir, exist_ok = True)
    os.makedirs(input_dir, exist_ok = True)
    files = ['config.yml','location.lst','workflows.yml']
    for i in files:
        shutil.copyfile(template_dir / i, run_dir / i)
    
    attrs = {"Source": "RFF",
            "Date Created": str(datetime.now()),
            "Description": (
            " Simulations based on parameters developed here: https://github.com/chrisroadmap/ar6/tree/main/notebooks."
            " Parameters obtained from: https://zenodo.org/record/5513022#.YVW1HZpByUk."),
        "Scenario": scenario,
        "Method": (
            "Temperature and ocean heat content were returned from fair.foward.fair_scm() in emission-driven mode."),
            "Note": "Code provided by Kelly McCusker of Rhodium Group Climate Impact Lab and adapted for use in FACTS."
        }

    t1 = xr.open_dataset('~/gcp_integration_archive_integration_econclim_data_climate_AR6_rff_ar6_rff_fair162_control_pulse_CO2_Fossil_2020-2030-2040-2050-2060-2070-2080_emis_conc_rf_temp_lambdaeff_ohc_emissions-driven_naturalfix_v5.03.nc')
    t1.close()
    if pulse_year == 'control':
        dat = (t1
            .drop_vars(['concentration', 'forcing', 'lambda_effective', 'rff_sp_index','climate_param_index'])
            .squeeze(drop = True)
            .rename(temperature = 'surface_temperature',year = 'years',runid  = 'samples')
            .sel(runtype = 'control',pulse_year = 2020, drop = True)
            .assign_coords(locations = -1)
            .expand_dims("locations")
        )
    else:
        dat = (t1
            .drop_vars(['concentration', 'forcing', 'lambda_effective', 'rff_sp_index','climate_param_index'])
            .squeeze(drop = True)
            .rename(temperature = 'surface_temperature',year = 'years',runid  = 'samples')
            .sel(runtype = 'pulse',pulse_year = pulse_year, drop = True)
            .assign_coords(locations = -1)
            .expand_dims("locations")
        )

    tempds = dat.surface_temperature.to_dataset()
    temps = tempds.surface_temperature.values
    ohcds = dat.ocean_heat_content.to_dataset()
    ohcs = ohcds.ocean_heat_content.values
    # Write the datasets to netCDF
    tempds.to_netcdf(input_dir / "gsat.nc4", encoding={"surface_temperature": {"dtype": "float64", "zlib": True, "complevel":4}})
    ohcds.to_netcdf(input_dir / "ohc.nc4", encoding={"ocean_heat_content": {"dtype": "float64", "zlib": True, "complevel":4}})

    # create a single netCDF file that is compatible with modules expecting parameters organized in a certain fashion
    pooledds = xr.Dataset({"surface_temperature": (("years","samples"), temps[0,::,::].transpose(), {"units":"degC"}),
                            "ocean_heat_content": (("years","samples"), ohcs[0,::,::].transpose(), {"units":"J"})},
        coords={"years": proj_years, "samples": np.arange(nsamps)+1}, attrs=attrs)
    pooledds.to_netcdf(input_dir / "climate.nc4", mode = 'w', group = scenario, engine = 'netcdf4', format = 'NETCDF4', encoding={"ocean_heat_content": {"dtype": "float64", "zlib": True, "complevel":4},
        "surface_temperature": {"dtype": "float64", "zlib": True, "complevel":4}})
    yearsds = xr.Dataset({"year": proj_years})
    yearsds.to_netcdf(input_dir / "climate.nc4", engine = 'netcdf4', format = 'NETCDF4', mode='a')
    
