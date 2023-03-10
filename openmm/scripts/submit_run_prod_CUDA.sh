#!/usr/bin/env bash
#SBATCH -t 24:00:00
#SBATCH --ntasks-per-node=1
#SBATCH --partition=gpu
#SBATCH --gpus=a100:1
#SBATCH --job-name=1anr
#SBATCH --mail-type=NONE    # Send email at begin and end of job
#SBATCH --output=job.out

source ~/.bashrc
source ../sourceme.sh
module load cuda
conda activate openmm

# supply pdbid and structure id as input
pdb=$1
structid=$2

# prefix is currently set to run included example
PREFIX="../example/yaml" 
master_yaml="${PREFIX}/master_prod.yaml"
sim_yaml="${PREFIX}/structure${structid}/sim_prod.yaml"

# you can edit the path to run_equil.py until I turn this into an actual package
python -u ../src/run_prod.py --master_yaml $master_yaml --sim_yaml $sim_yaml
