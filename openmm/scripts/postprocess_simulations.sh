#!/bin/bash
#SBATCH -t 02:00:00
#SBATCH --ntasks-per-node=8
#SBATCH --mem-per-cpu=10240
#SBATCH --job-name=p_traj
#SBATCH --mail-type=NONE    # Send email at begin and end of job
#SBATCH --output=outfiles/postprocess_sim.out

source $HOME/.bashrc
source ../sourceme.sh
# sourceme contains $CONDA and $PROJECT_PATH
#. "${CONDA_PREFIX_1}/etc/profile.d/conda.sh"
conda activate analysis

pdb=$1
root_path="${PROJECT_PATH}/${pdb}/${pdb}_iter0"
topology="${root_path}/${pdb}_nosol.pdb"
master_config="${root_path}/master_prod.yaml"
data_path="${PROJECT_PATH}/${pdb}/data/"

# change according to your file system
src_path="/home/lherron/scratch/repos/independent-simulations/openmm/src"

python -u ${src_path}/postprocess_simulations.py --root_path $root_path \
                                                 --data_path $data_path \
                                                 --topology $topology \
                                                 --master_config $master_config \
