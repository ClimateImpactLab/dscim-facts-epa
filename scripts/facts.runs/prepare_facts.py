import os
import xarray as xr
import numpy as np
import argparse
from datetime import datetime
from itertools import product
from pathlib import Path
import shutil
import argparse

# Create argument parser
parser = argparse.ArgumentParser(description='Process two lists.')

# Add named arguments for the lists
parser.add_argument('--facts_repo', nargs=1, help = 'Path to the FACTS repo')
parser.add_argument('--dscim_repo', nargs=1, help = 'Path to the FACTS repo')
parser.add_argument('--pulse_years', nargs='*', help='List of pulse years')
parser.add_argument('--gases', nargs='*', help='List of gases')


# Parse the command line arguments
args = parser.parse_args()

# Access the lists using the argument names
pulse_years = args.pulse_years
gases = args.gases
facts_dir = Path(args.facts_repo[0])
dscim_dir = Path(args.dscim_repo[0])
print("Facts_dir:", facts_dir)
print("pulse_years:", pulse_years)
print("gases:", gases)

scenario = 'ssp245'
nsamps = 10000


for pulse_year, gas in list(product(pulse_years,gases)) + [('control','control'),]:
    template_dir = Path(os.getcwd()) / 'template'
    
    # FACTS does not accept underscores in experiment names
    gas_exp = gas.replace('_','.')
    
    run_dir = facts_dir / f'rff.{pulse_year}.{gas_exp}'
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

    temp_file = xr.open_dataset(dscim_dir/'scripts'/'input'/'climate'/'gmst_pulse.nc4')
    ohc_file = xr.open_dataset(dscim_dir/'scripts'/'input'/'climate'/'ohc_pulse.nc4')
    proj_years = temp_file.year.values.flatten()

    temp_file.close()
    ohc_file.close()
    if pulse_year == 'control':
        tempds = (temp_file
            .rename(control_temperature = 'surface_temperature',year = 'years',runid  = 'samples')
            .assign_coords(locations = -1)
            .expand_dims("locations")
        ).surface_temperature.to_dataset()
        
        ohcds = (ohc_file
            .rename(control_ocean_heat_content = 'ocean_heat_content',year = 'years',runid  = 'samples')
            .assign_coords(locations = -1)
            .expand_dims("locations")
        ).ocean_heat_content.to_dataset()
    else:
        tempds = (temp_file
            .rename(pulse_temperature = 'surface_temperature',year = 'years',runid  = 'samples')
            .sel(pulse_year = int(pulse_year), gas = gas, drop = True)
            .assign_coords(locations = -1)
            .expand_dims("locations")
        ).surface_temperature.to_dataset()
        
        ohcds = (ohc_file
            .rename(pulse_ocean_heat_content = 'ocean_heat_content',year = 'years',runid  = 'samples')
            .sel(pulse_year = int(pulse_year), gas = gas, drop = True)
            .assign_coords(locations = -1)
            .expand_dims("locations")
        ).ocean_heat_content.to_dataset()

    temps = tempds.surface_temperature.values
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
    
