#!/usr/bin/env bash
#SBATCH -t 12:00:00
#SBATCH --ntasks-per-node=1
#SBATCH --partition=gpu
#SBATCH --gpus=a100:1
#SBATCH --job-name=equil
#SBATCH --mail-type=NONE    # Send email at begin and end of job
#SBATCH --output=outfiles/equil.out

source $HOME/.bashrc
source ../sourceme.sh
# sourceme contains $CONDA and $PROJECT_PATH
#. "${CONDA_PREFIX_1}/etc/profile.d/conda.sh"
conda activate analysis

module purge
module load cuda

pdb=$1
structid=$2

master_config="/home/lherron/scratch/RNAfold/${pdb}/${pdb}_iter0/master_equil.yaml"
sim_config="/home/lherron/scratch/RNAfold/${pdb}/${pdb}_iter0/struct${structid}/sim_equil.yaml"

python -u ../src/equilibration.py --master_config $master_config --sim_config $sim_config
