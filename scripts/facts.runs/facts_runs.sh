#!/bin/bash
# Set overwrite to 1 to overwrite previous results (if they exist), 0 otherwise
overwrite=0
# Define arrays for pulse years and gases
# Additional pulse years and gases can be appended with spaces in between
# example: pulse_years=(2020 2030 2040)
# example: gases=("CO2_Fossil" "CH4" "N2O")
pulse_years=(2020)
gases=("CO2_Fossil")
facts_dir="/opt/facts"
dscim_facts_epa_dir="/opt/dscim-facts-epa"
# Create FACTS experiments
python3 prepare_facts.py --dscim_repo "${dscim_facts_epa_dir}" --facts_repo "${facts_dir}" --pulse_years "${pulse_years[@]}" --gases "${gases[@]}"
# Loop through the pulse years
for gas in "${gases[@]}"; do
    # Loop through the gases
    for year in "${pulse_years[@]}"; do    
        echo "Gas: $gas"
        echo "Pulse: $year"
        wfs=0
        gas_exp="${gas//_/.}"
        # Check if experiment output files have already been generated
        if [ -f $facts_dir/experiments/rff.$year.$gas_exp/output/rff.$year.$gas_exp.total.workflow.wf1f.global.nc ]; then
            wfs=$((wfs + 1))
        fi
        if [ -f $facts_dir/experiments/rff.$year.$gas_exp/output/rff.$year.$gas_exp.total.workflow.wf2f.global.nc ]; then
            wfs=$((wfs + 1))
        fi
        if (( $wfs != 2 | $overwrite == 1 )); then
            cd $facts_dir
            python3 runFACTS.py experiments/rff.$year.$gas_exp
        else 
            echo "experiment results found, not rerunning"
        fi
    done
done
echo "Generating control run GMSL"
wfs=0
if [ -f $facts_dir/experiments/rff.control.control/output/rff.control.control.total.workflow.wf1f.global.nc ]; then
    wfs=$((wfs + 1))
fi
if [ -f $facts_dir/experiments/rff.control.control/output/rff.control.control.total.workflow.wf2f.global.nc ]; then
    wfs=$((wfs + 1))
fi
if (( $wfs != 2 | $overwrite == 1 )); then
    cd $facts_dir
    python3 runFACTS.py experiments/rff.control.control
else 
    echo "experiment results found, not rerunning"
fi
cd $dscim_facts_epa_dir/scripts/facts.runs
# Take the outputs of the FACTS experiment and save in the proper format
python3 format_facts.py --facts_repo "${facts_dir}" --pulse_years "${pulse_years[@]}" --gases "${gases[@]}" --gmsl_pulse facts_gmsl_pulse.nc4
cd $dscim_facts_epa_dir/scripts
# Create config for dscim run
python3 create_config.py --gmsl_file facts_gmsl_pulse.nc4 --gmst_file gmst_pulse.nc4 --pulse_years "${pulse_years[@]}" --gases "${gases[@]}"
