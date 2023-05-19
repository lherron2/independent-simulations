#!/bin/bash
#SBATCH -t 06:00:00
#SBATCH --ntasks-per-node=32
#SBATCH --mem-per-cpu=10240
#SBATCH --job-name=p_diff
#SBATCH --mail-type=NONE    # Send email at begin and end of job
#SBATCH --output=outfiles/postprocess_diff.out

source $HOME/.bashrc
source ../sourceme.sh
# sourceme contains $CONDA and $PROJECT_PATH
. "$CONDA/etc/profile.d/conda.sh"
conda activate analysis

pdb=$1
diffusion_path="/home/lherron/scratch/repos/thermodynamic-diffusion/systems/${pdb}/experiments/gvecs/10us/samples"
data_path="${PROJECT_PATH}/${pdb}/data"
subsample=1

# change according to your file system
src_path="/home/lherron/scratch/repos/independent-simulations/openmm/src"

python -u ${src_path}/postprocess_diffusion.py --pdbid $pdb \
                                               --diffusion_path $diffusion_path \
                                               --subsample $subsample \
                                               --data_path $data_path

