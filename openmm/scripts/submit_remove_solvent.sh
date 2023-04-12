#!/bin/bash
#SBATCH -t 00:30:00
#SBATCH --ntasks-per-node=1
#SBATCH --job-name=nosol
#SBATCH --mail-type=NONE    # Send email at begin and end of job
#SBATCH --output=nosol.out

source ~/.bashrc
source ../sourceme.sh
conda activate openmm

pdb=$1
structid=$2

# change according to your file system
PREFIX="../example" 
master_yaml="${PREFIX}/yaml/master_prod.yaml"
src_path="/home/lherron/scratch/repos/independent-simulations/openmm/src"

python -u ${src_path}/remove_solvent.py --pdbid $pdb --structid $structid --master_yaml $master_yaml
