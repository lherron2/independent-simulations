#!/bin/bash
#SBATCH -t 48:00:00
#SBATCH --ntasks-per-node=1
#SBATCH --job-name=fold
#SBATCH --mail-type=NONE    # Send email at begin and end of job
#SBATCH --output=1anr_pot.out

. "/home/lherron/scratch.tiwary-prj/miniconda/etc/profile.d/conda.sh"
conda activate analysis

pdb=$1
structid=$2
rad=5
base_path="/home/lherron/scratch/RNAfold/${pdb}/replicas/structure${structid}"

python -u ../src/compute_potential_energy.py --pdbid $pdb --structid $structid --rad $rad --base_path $base_path
