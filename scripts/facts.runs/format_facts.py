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
import argparse

# Create argument parser
parser = argparse.ArgumentParser(description='Process two lists.')

# Add named arguments for the lists
parser.add_argument('--facts_repo',nargs ='*', help = 'Path to the FACTS repo')
parser.add_argument('--pulse_years', nargs='*', help='List of pulse years')
parser.add_argument('--gases', nargs='*', help='List of gases')

# Parse the command line arguments
args = parser.parse_args()

# Access the lists using the argument names
pulse_years = args.pulse_years
gases = args.gases
facts_dir = args.facts_repo

print("pulse_years:", pulse_years)
print("gases:", gases)



control = (0.5 * xr.open_dataset(facts_dir + '/rff.control.control/output/rff.control.control.total.workflow.wf1f.global.nc') +
    0.5 * xr.open_dataset(facts_dir + '/rff.control.control/output/rff.control.control.total.workflow.wf2f.global.nc'))

nsamps = len(control.samples.values)
     
pulse_gas = []
for pulse_year, gas in list(product(pulse_years,gases))
    pulse = (0.5 * xr.open_dataset(facts_dir + f'/rff.{pulse_year}.{gas}/output/rff.{pulse_year}.{gas}.total.workflow.wf1f.global.nc') +
        0.5 * xr.open_dataset(facts_dir + f'/rff.{pulse_year}.{gas}/output/rff.{pulse_year}.{gas}.total.workflow.wf2f.global.nc')
             .assign_coords({'runid':np.arange(1,nsamps + 1),'gas':gas, 'pulse_year':pulse_year})
             .expand_dims(['gas','pulse_year'])
            )
    pulse_gas = pulse_gas + [pulse,]
pulse = xr.concat(pulse_gas)
    
pulse = (pulse
         .squeeze(drop = True)
         .rename({'samples':'runid','sea_level_change':'pulse_gmsl','years':'year'})
         .assign_coords({'runid':np.arange(1,nsamps + 1),'gas':'CO2_Fossil', 'pulse_year':2020})
         .expand_dims(['gas','pulse_year'])
         .drop(['lat','lon'])
        )
control = (control
           .squeeze(drop = True)
           .rename({'samples':'runid','sea_level_change':'control_gmsl','years':'year'})
           .assign_coords({'runid':np.arange(1,nsamps + 1)})
           .drop(['lat','lon']))

gmsl_ds = xr.merge([control,pulse])/10

save = Path(os.getcwd())
save = save.parent.absolute() / 'input' / 'climate

gmsl_ds.to_netcdf(save / 'gmsl_pulse.nc4', encoding = {"control_gmsl":{"dtype":"float64"},"pulse_gmsl":{"dtype":"float64"}})
    