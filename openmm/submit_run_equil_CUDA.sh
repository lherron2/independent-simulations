#!/bin/bash
#SBATCH -t 12:00:00
#SBATCH --ntasks-per-node=1
#SBATCH --partition=gpu
#SBATCH --gpus=a100:1
#SBATCH --job-name=1anr
#SBATCH --mail-type=NONE    # Send email at begin and end of job
#SBATCH --output=job.out

. "/home/lherron/scratch.tiwary-prj/miniconda/etc/profile.d/conda.sh"
conda activate openmm

pdb=$1
structid=$2

master_yaml="/home/lherron/scratch/RNAfold/${pdb}/replicas/master_equil.yaml"
sim_yaml="/home/lherron/scratch/RNAfold/${pdb}/replicas/structure${structid}/sim_equil.yaml"

python -u run_equil.py --master_yaml $master_yaml --sim_yaml $sim_yaml
