#!/bin/bash
#SBATCH -t 02:00:00
#SBATCH --ntasks-per-node=24
#SBATCH --mem-per-cpu=10240
#SBATCH --job-name=dataset
#SBATCH --mail-type=NONE    # Send email at begin and end of job
#SBATCH --output=outfiles/dataset.out

source $HOME/.bashrc
source ../sourceme.sh
# sourceme contains $CONDA and $PROJECT_PATH
#. "${CONDA_PREFIX_1}/etc/profile.d/conda.sh"
conda activate analysis

pdb=$1
gvec_path="${PROJECT_PATH}/${pdb}/data/${pdb}_MD_gvecs.npy"
dataset_path="${PROJECT_PATH}/${pdb}/data/${pdb}_gvec_dataset.npy"

# change according to your file system
src_path="/home/lherron/scratch/repos/independent-simulations/openmm/src"

python -u ${src_path}/gvec_to_dataset.py --gvec_path $gvec_path \
                                         --dataset_path $dataset_path \
