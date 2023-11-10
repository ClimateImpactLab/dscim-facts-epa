import yaml
import os
from pathlib import Path
from datetime import datetime
import sys
import re
import argparse

# Create argument parser
parser = argparse.ArgumentParser(description='Create config from gmsl and gmst pulse files')

# Add named arguments for the lists
parser.add_argument('--gmsl_pulse', nargs=1, help='Path to GMSL pulse file')
parser.add_argument('--gmst_pulse', nargs=1, help='Path to GMST pulse file')

# Parse the command line arguments
args = parser.parse_args()

# Access the lists using the argument names
gmsl_pulsename = args.gmsl_pulse
gmst_pulsename = args.gmst_pulse

currentDay = datetime.now().day
currentMonth = datetime.now().month
currentYear = datetime.now().year

args = sys.argv
if len(args) == 1:
    gmst_pulsename = "gmst_pulse.nc4"
    gmsl_pulsename = "gmsl_pulse.nc4"
else:
    gmst_pulsename = args[1]
    gmsl_pulsename = args[2]


# We may want to read these files in to make sure they exist/have the correct format

base = os.getcwd()
input = Path(base) / "input"  
output = Path(base) / "output"  


climate_inputs = input / "climate"
econ_inputs = input / "econ"
damage_functions = input / "damage_functions"

conf_base = {'mortality_version': 1,
             'coastal_version': '0.20',
             'rff_climate': {'gases': ['CO2_Fossil', 'CH4', 'N2O'],
                             'gmsl_path': '',
                             'gmst_path': '',
                             'gmst_fair_path': str(climate_inputs / gmst_pulsename),
                             'gmsl_fair_path': str(climate_inputs / gmsl_pulsename),
                             'damages_pulse_conversion_path': str(climate_inputs / 'conversion_v5.03_Feb072022.nc4'),
                             'ecs_mask_path': None,
                             'emission_scenarios': None},
             'paths': {'rff_damage_function_library': str(damage_functions)},
             'rffdata': {'socioec_output': str(econ_inputs),
                         'pulse_years': [2020, 2030, 2040, 2050, 2060, 2070, 2080]},
             'sectors': {'coastal_v0.20': {'formula': 'damages ~ -1 + gmsl + np.power(gmsl, 2)'},
                         'agriculture': {'formula': 'damages ~ -1 + anomaly + np.power(anomaly, 2)'},
                         'mortality_v1': {'formula': 'damages ~ -1 + anomaly + np.power(anomaly, 2)'},
                         'energy': {'formula': 'damages ~ -1 + anomaly + np.power(anomaly, 2)'},
                         'labor': {'formula': 'damages ~ -1 + anomaly + np.power(anomaly, 2)'},
                         'AMEL_m1': {'formula': 'damages ~ -1 + anomaly + np.power(anomaly, 2)'},
                         'CAMEL_m1_c0.20': {'formula': 'damages ~ -1 + anomaly + np.power(anomaly, 2) + gmsl + np.power(gmsl, 2)'}},
             'save_path': str(output)}


if os.path.exists(f"facts_conf_{currentDay}-{currentMonth}-{currentYear}.yaml"):
    files = os.listdir('.')

    def find_filenum(f):
        num = re.findall(f"facts_conf_{currentDay}-{currentMonth}-{currentYear}_(\d+).yaml",f)
        return int(num[0]) if num else 1

    i = max(map(find_filenum, files)) + 1

    config_file = f"facts_conf_{currentDay}-{currentMonth}-{currentYear}_{i}.yaml"
else:
    config_file = f"facts_conf_{currentDay}-{currentMonth}-{currentYear}.yaml"


with open(config_file, 'w') as outfile:
    yaml.dump(conf_base, outfile, default_flow_style=False)

print(f"Saved config to {config_file}")
print(f"To run SC-GHGs, use the command")
print(f"python command_line_scghg.py {config_file}")