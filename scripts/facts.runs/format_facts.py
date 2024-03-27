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

# Create argument parser
parser = argparse.ArgumentParser(description='Process lists of gases and pulse years to get experiments from FACTS')

# Add named arguments for the lists
parser.add_argument('--facts_repo', nargs=1, help = 'Path to the FACTS repo')
parser.add_argument('--pulse_years', nargs='*', help='List of pulse years')
parser.add_argument('--gases', nargs='*', help='List of gases')
parser.add_argument('--gmsl_pulse', nargs=1, help='gmsl pulse filename to save out')

# Parse the command line arguments
args = parser.parse_args()

# Access the lists using the argument names
facts_dir = args.facts_repo[0]
gmsl_pulse = args.gmsl_pulse[0]

if args.pulse_years:
    pulse_years = list(map(int, args.pulse_years))
else:
    print("No pulse years specified")
    print("Defaulting to 2020 pulse year")
    pulse_years = [2020]

if args.gases:
    gases = args.gases
else:
    print("No gases specified")
    print("Defaulting to CO2_Fossil")
    gases = ['CO2_Fossil']


print("pulse_years:", pulse_years)
print("gases:", gases)



control = (0.5 * xr.open_dataset(facts_dir + '/experiments/rff.control.control/output/rff.control.control.total.workflow.wf1f.global.nc') +
    0.5 * xr.open_dataset(facts_dir + '/experiments/rff.control.control/output/rff.control.control.total.workflow.wf2f.global.nc'))

nsamps = len(control.samples.values)
     
pulse_gas = []
for pulse_year, gas in list(product(pulse_years,gases)):
    gas_exp = gas.replace('_','.')
    pulse = ((0.5 * xr.open_dataset(facts_dir + f'/experiments/rff.{pulse_year}.{gas_exp}/output/rff.{pulse_year}.{gas_exp}.total.workflow.wf1f.global.nc') +
        0.5 * xr.open_dataset(facts_dir + f'/experiments/rff.{pulse_year}.{gas_exp}/output/rff.{pulse_year}.{gas_exp}.total.workflow.wf2f.global.nc'))
             .rename({'samples':'runid','sea_level_change':'pulse_gmsl','years':'year'})
             .assign_coords({'runid':np.arange(1,nsamps + 1),'gas':gas, 'pulse_year':int(pulse_year)})
             .expand_dims(['gas','pulse_year'])
            )
    pulse_gas = pulse_gas + [pulse,]
pulse = xr.combine_by_coords(pulse_gas)
    
pulse = (pulse
         .drop(['lat','lon','locations'])
        )

control = (control
           .squeeze(drop = True)
           .rename({'samples':'runid','sea_level_change':'control_gmsl','years':'year'})
           .assign_coords({'runid':np.arange(1,nsamps + 1)})
           .drop(['lat','lon']))

gmsl_ds = xr.merge([control,pulse])/10

save = Path(os.getcwd())
save = save.parent.absolute() / 'input' / 'climate'

gmsl_ds.to_netcdf(save / gmsl_pulse, encoding = {"control_gmsl":{"dtype":"float64"},"pulse_gmsl":{"dtype":"float64"}})
    