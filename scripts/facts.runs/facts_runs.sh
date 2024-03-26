#!/bin/bash
# Define arrays for pulse years and gases
# Additional pulse years and gases can be appended with spaces in between
# example: pulse_years=(2020 2030 2040)
# example: gases=("CO2_Fossil" "CH4" "N2O")
pulse_years=(2020)
gases=("CO2_Fossil")
# Desired control/pulse file paths
gmst_file="/opt/dscim-facts-epa/scripts/input/climate/gmst_pulse.nc4"
ohc_file="/opt/dscim-facts-epa/scripts/input/climate/ohc_pulse.nc4"
# Desired GMSL pulse file path
gmsl_file="/opt/dscim-facts-epa/scripts/input/climate/facts_gmsl_pulse.nc4"
# Paths to directories
facts_dir="/opt/facts"
dscim_facts_epa_dir="/opt/dscim-facts-epa"
# Create FACTS experiments
# python3 prepare_facts.py \
#  --dscim_repo "${dscim_facts_epa_dir}" \
#  --facts_repo "${facts_dir}" \
#  --pulse_years "${pulse_years[@]}" \
#  --gases "${gases[@]}" \
#  --gmst_file $gmst_file \
#  --ohc_file $ohc_file 
# # Loop through the pulse years
# for gas in "${gases[@]}"; do
#     # Loop through the gases
#     for year in "${pulse_years[@]}"; do    
#         gas_exp="${gas//_/.}"
#         echo "Gas: $gas"
# 	    echo "Pulse: $year"
#         cd $facts_dir
#         python3 runFACTS.py rff.$year.$gas_exp
#     done
# done
# python3 runFACTS.py rff.control.control
cd $dscim_facts_epa_dir/scripts/facts.runs
# Take the outputs of the FACTS experiment and save in the proper format
python3 format_facts.py \
--facts_repo "${facts_dir}" \
--pulse_years "${pulse_years[@]}" \
--gases "${gases[@]}" \
--gmsl_file $gmsl_file
cd $dscim_facts_epa_dir/scripts
# Create config for dscim run
python3 create_config.py \
--gmsl_file $gmsl_file \
--gmst_file $gmst_file \
--pulse_years "${pulse_years[@]}" \
--gases "${gases[@]}" 
