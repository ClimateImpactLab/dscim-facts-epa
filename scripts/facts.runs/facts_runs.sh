#!/bin/bash

# Define arrays for pulse years and gases
pulse_years=(2020)
gases=("CO2_Fossil")

facts_dir= "/home/jonahmgilbert/repos/facts"

# Create FACTS experiments
python prepare_facts.py --facts-repo "${facts_dir}" --pulse_years "${pulse_years[@]}" --gases "${gases[@]}"

# Loop through the pulse years
for gas in "${gases[@]}"; do
    # Loop through the gases
    for year in "${pulse_years[@]}"; do    
        echo "Gas: $gas"
	    echo "Pulse: $year"
        cd ~/repos/facts/
        python3 ~/repos/facts/runFACTS.py ~/repos/facts/rff.$year.$gas
    done
done


# Take the outputs of the FACTS experiment and save in the proper format
python format_facts.py --facts-repo "${facts_dir}" --pulse_years "${pulse_years[@]}" --gases "${gases[@]}"

# Create config for dscim run
