#!/bin/bash
#SBATCH -t 06:00:00
#SBATCH --ntasks-per-node=2
#SBATCH --mem-per-cpu=10240
#SBATCH --job-name=nosol
#SBATCH --mail-type=NONE    # Send email at begin and end of job
#SBATCH --output=outfiles/nosol.out

source $HOME/.bashrc
source ../sourceme.sh
# sourceme contains $CONDA and $PROJECT_PATH
#. "${CONDA_PREFIX_1}/etc/profile.d/conda.sh"
conda activate analysis

pdb=$1
structid=$2

master_config="${PROJECT_PATH}/${pdb}/${pdb}_iter0/master_prod.yaml" 
sim_config="${PROJECT_PATH}/${pdb}/${pdb}_iter0/struct${structid}/sim_prod.yaml"

# change according to your file system
src_path="/home/lherron/scratch/repos/independent-simulations/openmm/src"
subsample=10

python -u ${src_path}/trjcat.py --master_config $master_config \
                                --sim_config $sim_config \
                                --subsample $subsample \
                                --chunk_size 10 \
                                --desolvate True \

