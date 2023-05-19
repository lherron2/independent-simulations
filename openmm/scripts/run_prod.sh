#!/usr/bin/env bash
#SBATCH -t 120:00:00
#SBATCH --ntasks-per-node=1
#SBATCH --partition=scavenger
#SBATCH --gpus=a100:1
#SBATCH --job-name=1anr
#SBATCH --mail-type=NONE    # Send email at begin and end of job
#SBATCH --output=job.out

source $HOME/.bashrc
source ../sourceme.sh
# sourceme contains $CONDA and $PROJECT_PATH
#. "${CONDA_PREFIX_1}/etc/profile.d/conda.sh"
conda activate analysis

module purge
module load cuda


pdb=$1
structid=$2

master_config="/home/lherron/scratch/RNAfold/${pdb}/${pdb}_iter0/master_prod.yaml"
sim_config="/home/lherron/scratch/RNAfold/${pdb}/${pdb}_iter0/struct${structid}/sim_prod.yaml"

../src/simulate.py --master_config $master_config --sim_config $sim_config
