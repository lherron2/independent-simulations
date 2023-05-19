#!/bin/bash
#SBATCH -t 00:30:00
#SBATCH --ntasks-per-node=24
#SBATCH --mem-per-cpu=10240
#SBATCH --job-name=pca
#SBATCH --mail-type=NONE    # Send email at begin and end of job
#SBATCH --output=outfiles/pca.out

source $HOME/.bashrc
source ../sourceme.sh
# sourceme contains $CONDA and $PROJECT_PATH
#. "${CONDA_PREFIX_1}/etc/profile.d/conda.sh"
conda activate analysis

pdb=$1
data_path="${PROJECT_PATH}/${pdb}/data"

# change according to your file system
src_path="/home/lherron/scratch/repos/independent-simulations/openmm/src"

python -u ${src_path}/joint_PCA.py --pdbid $pdb \
                                   --data_path $data_path
