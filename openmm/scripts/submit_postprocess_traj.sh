#!/bin/bash
#SBATCH -t 02:00:00
#SBATCH --ntasks-per-node=8
#SBATCH --mem-per-cpu=10240
#SBATCH --job-name=p_traj
#SBATCH --mail-type=NONE    # Send email at begin and end of job
#SBATCH --output=traj_postprocess.out

source ~/.bashrc
source ../sourceme.sh
conda activate analysis

pdb=$1
project_path="/home/lherron/scratch/RNAfold"
root_path="${project_path}/${pdb}/replicas"
data_path="${project_path}/${pdb}/data"
diffusion_path="${project_path}/${pdb}/DDIM/samples"
topology_path="${root_path}/${pdb}_nosol.pdb"
master_yaml="${root_path}/master_prod.yaml"

# change according to your file system
src_path="/home/lherron/scratch/repos/independent-simulations/openmm/src"

python -u ${src_path}/postprocess_traj.py --pdbid $pdb \
                                          --root_path $root_path \
                                          --data_path $data_path \
                                          --diffusion_path $diffusion_path\
                                          --topology_path $topology_path\
                                          --master_yaml $master_yaml
