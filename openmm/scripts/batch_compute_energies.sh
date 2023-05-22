#!/bin/bash

pdbids=(
#"1zih"
"5udz"
#"1anr"
)

rads=(
"0"
"2.5"
"5"
)

for pdb in "${pdbids[@]}"; do
    for rad in "${rads[@]}"; do
        for i in {0..49}; do 
            echo $pdb $rad $i
            sbatch compute_solvated_energy.sh --pdb $pdb --structid $i --rad $rad;
            sleep 0.1
        done
    done
done
