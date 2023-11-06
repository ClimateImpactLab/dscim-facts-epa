#!/bin/bash

# Define arrays for pulse years and gases
pulse_years=("control" 2020)
gases=("CO2")

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

