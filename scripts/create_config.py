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
parser.add_argument('--gmsl_file', type=str, help='Path to GMSL pulse file')
parser.add_argument('--gmst_file', type=str, help='Path to GMST pulse file')
parser.add_argument('--pulse_years', nargs='*', help='List of pulse years')
parser.add_argument('--gases', nargs='*', help='List of gases')
parser.add_argument('--input_dir', type=str, default="/opt/dscim-facts-epa/scripts/input", help='Path to inputs directory')
parser.add_argument('--output_dir', type=str, default="/opt/dscim-facts-epa/scripts/output", help='Path to outputs directory')
parser.add_argument('--config_dir', type=str, default="/opt/dscim-facts-epa/scripts", help='Path to config directory')

# Parse the command line arguments
args = parser.parse_args()
# Access the lists using the argument names
gmsl_path = Path(args.gmsl_file)
gmst_path = Path(args.gmst_file)
input_dir = Path(args.input_dir)
output_dir = Path(args.output_dir)
config_dir = Path(args.config_dir)

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

print(pulse_years)
print(gases)

currentDay = datetime.now().day
currentMonth = datetime.now().month
currentYear = datetime.now().year


# We may want to read these files in to make sure they exist/have the correct format

base = os.getcwd()
input = input_dir 
output = output_dir
config = config_dir

climate_inputs = input / "climate"
econ_inputs = input / "econ"
damage_functions = input / "damage_functions"

conf_base = {'mortality_version': 1,
             'coastal_version': '0.20',
             'rff_climate': {'gases': gases,
                             'gmsl_path': '',
                             'gmst_path': '',
                             'gmst_fair_path': str(gmst_path),
                             'gmsl_fair_path': str(gmsl_path),
                             'damages_pulse_conversion_path': str(climate_inputs) + '/conversion_v5.03_Feb072022.nc4',
                             'ecs_mask_path': None,
                             'emission_scenarios': None},
             'paths': {'rff_damage_function_library': str(damage_functions)},
             'rffdata': {'socioec_output': str(econ_inputs),
                         'pulse_years': pulse_years},
             'sectors': {'coastal_v0.20': {'formula': 'damages ~ -1 + gmsl + np.power(gmsl, 2)'},
                         'agriculture': {'formula': 'damages ~ -1 + anomaly + np.power(anomaly, 2)'},
                         'mortality_v1': {'formula': 'damages ~ -1 + anomaly + np.power(anomaly, 2)'},
                         'energy': {'formula': 'damages ~ -1 + anomaly + np.power(anomaly, 2)'},
                         'labor': {'formula': 'damages ~ -1 + anomaly + np.power(anomaly, 2)'},
                         'AMEL_m1': {'formula': 'damages ~ -1 + anomaly + np.power(anomaly, 2)'},
                         'CAMEL_m1_c0.20': {'formula': 'damages ~ -1 + anomaly + np.power(anomaly, 2) + gmsl + np.power(gmsl, 2)'}},
             'save_path': str(output),
             'gas_conversions':{
                 'CO2_Fossil': 2.72916487e-10,
                 'CH4': 2.50000000e-08,
                 'N2O': 6.36480131e-07}}


if os.path.exists(config / f"facts_conf_{currentDay}-{currentMonth}-{currentYear}.yaml"):
    files = os.listdir('.')

    def find_filenum(f):
        num = re.findall(f"facts_conf_{currentDay}-{currentMonth}-{currentYear}_(\d+).yaml",f)
        return int(num[0]) if num else 1

    i = max(map(find_filenum, files)) + 1

    config_file = config / f"facts_conf_{currentDay}-{currentMonth}-{currentYear}_{i}.yaml"
else:
    config_file = config / f"facts_conf_{currentDay}-{currentMonth}-{currentYear}.yaml"


with open(config_file, 'w') as outfile:
    yaml.dump(conf_base, outfile, default_flow_style=False)

print(f"Saved config to {config_file}")
print(f"To run SC-GHGs, use the command")
print(f"python command_line_scghg.py {config_file}")