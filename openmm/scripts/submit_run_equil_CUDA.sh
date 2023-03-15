#!/usr/bin/env bash
#SBATCH -t 12:00:00
#SBATCH --ntasks-per-node=1
#SBATCH --partition=gpu
#SBATCH --gpus=a100:1
#SBATCH --job-name=1anr
#SBATCH --mail-type=NONE    # Send email at begin and end of job
#SBATCH --output=job.out

source $HOME/.bashrc
source ../sourceme.sh
module purge
module load cuda
conda activate openmm

# supply pdbid and structure id as input
pdb=$1 
structid=$2

# prefix is currently set to run included example
PREFIX="../example" 
master_yaml="${PREFIX}/yaml/master_equil.yaml"
sim_yaml="${PREFIX}/struct${structid}/sim_equil.yaml"

echo $master_yaml
echo $sim_yaml

# you can edit the path to run_equil.py from other locations until I turn 
# this into an actual package.
run_equil.py --master_yaml $master_yaml --sim_yaml $sim_yaml
