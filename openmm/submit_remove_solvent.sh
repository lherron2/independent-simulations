#!/bin/bash
#SBATCH -t 00:10:00
#SBATCH --ntasks-per-node=1
#SBATCH --job-name=fold
#SBATCH --mail-type=NONE    # Send email at begin and end of job
#SBATCH --output=None

. "/home/lherron/scratch.tiwary-prj/miniconda/etc/profile.d/conda.sh"
conda activate openmm

pdb=$1
structid=$2

python -u remove_solvent.py --pdbid $pdb --structid $structid
