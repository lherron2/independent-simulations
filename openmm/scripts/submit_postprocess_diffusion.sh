#!/bin/bash
#SBATCH -t 00:30:00
#SBATCH --ntasks-per-node=8
#SBATCH --mem-per-cpu=10240
#SBATCH --job-name=p_diff
#SBATCH --mail-type=NONE    # Send email at begin and end of job
#SBATCH --output=diff_postprocess.out

source ~/.bashrc
source ../sourceme.sh
conda activate analysis

pdb=$1

project_path="/home/lherron/scratch/RNAfold"
#diffusion_path="${project_path}/${pdb}/DDIM/samples"
diffusion_path="/home/lherron/scratch/repos/thermodynamic-diffusion/systems/${pdb}/experiments/gvecs/x0_mid_attn_sc/samples"
data_path="${project_path}/${pdb}/data"

# change according to your file system
src_path="/home/lherron/scratch/repos/independent-simulations/openmm/src"

python -u ${src_path}/postprocess_diffusion.py --pdbid $pdb \
                                               --diffusion_path $diffusion_path \
                                               --data_path $data_path

