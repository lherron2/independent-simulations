#!/bin/bash
#SBATCH -t 16:00:00
#SBATCH --ntasks-per-node=1
#SBATCH --job-name=energies
#SBATCH --mail-type=NONE    # Send email at begin and end of job
#SBATCH --output=energies.out

source $HOME/.bashrc
source ../sourceme.sh
# sourceme contains $CONDA and $PROJECT_PATH
#. "${CONDA_PREFIX_1}/etc/profile.d/conda.sh"
conda activate analysis

# INPUTS
pdb=$1
structid=$2
rad=$3
selection="resname [GACU]"

# paths to simulation outputs
identifier="struct"
name_prefix="${pdb}_${identifier}${structid}"
topology="${PROJECT_PATH}/${pdb}/${pdb}_iter0/${identifier}${structid}/${name_prefix}_sol.pdb"
trajectory="${PROJECT_PATH}/${pdb}/${pdb}_iter0/${identifier}${structid}/${name_prefix}_sol.xtc"

# force fields
solute_forcefield="amber14/RNA.Shaw_charmm22-ions.xml"
solvent_forcefield="amber14/tip4pd_desres.xml"

# output file
outfile="${PROJECT_PATH}/${pdb}/${pdb}_iter0/${identifier}${structid}/${name_prefix}_r=${rad}_energies.npy"

python -u ../src/eval_ff.py --rad $rad \
                            --sel "${selection}" \
                            --top $topology \
                            --traj $trajectory \
                            --solute_ff $solute_forcefield \
                            --solvent_ff $solvent_forcefield \
                            --outfile $outfile \

