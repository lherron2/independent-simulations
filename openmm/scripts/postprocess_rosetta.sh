#!/bin/bash
#SBATCH -t 16:00:00
#SBATCH --ntasks-per-node=1
#SBATCH --job-name=p_rosetta
#SBATCH --mail-type=NONE    # Send email at begin and end of job
#SBATCH --output=outfiles/postprocess_rosetta.out

source $HOME/.bashrc
source ../sourceme.sh
# sourceme contains $CONDA and $PROJECT_PATH
#. "${CONDA_PREFIX_1}/etc/profile.d/conda.sh"
conda activate analysis

pdb=$1

### FIXING BROKEN ROSETTA TRAJECTORIES ###

# edit these:
broken_traj="${PROJECT_PATH}/${pdb}/rosetta/${pdb}.xtc"
broken_top="${PROJECT_PATH}/${pdb}/rosetta/${pdb}_top.pdb"


# do not edit these:
fixed_traj="${PROJECT_PATH}/${pdb}/rosetta/${pdb}_fixed.xtc"
fixed_top="${PROJECT_PATH}/${pdb}/rosetta/${pdb}_top_fixed.pdb"

python -u ../src/fix_traj.py --broken_traj $broken_traj \
                            --broken_top $broken_top \
                            --fixed_traj $fixed_traj \
                            --fixed_top $fixed_top \
#

### COMPUTING GVECS FOR FIXED TRAJECTORIES ###

mkdir -p "${PROJECT_PATH}/${pdb}/data"
gvec_file="${PROJECT_PATH}/${pdb}/data/${pdb}_rosetta_gvecs.npy"

#python -u ../src/compute_gvecs.py --traj $fixed_traj \
#                                  --top $fixed_top \
#                                  --outfile $gvec_file \

### COMPUTING ANNOTATIONS FOR FIXED TRAJECTORIES ###

annot_file="${PROJECT_PATH}/${pdb}/data/${pdb}_rosetta_annot.npy"

python -u ../src/annotate_traj.py --traj $fixed_traj \
                                  --top $fixed_top \
                                  --outfile $annot_file \

solute_forcefield="amber14/RNA.Shaw_charmm22-ions.xml"

### COMPUTING ENERGIES W/ IMPLICIT SOLVENT ###

#solvent_forcefield="implicit/gbn2.xml"
#outfile="${PROJECT_PATH}/${pdb}/data/${pdb}_rosetta_sol_energies.npy"
#
#python -u ../src/compute_solvated_potential.py --pdbid $pdb \
#                                               --rad 0 \
#                                               --selection 'resname [GACU]' \
#                                               --topology $fixed_top \
#                                               --trajectory $fixed_traj \
#                                               --solute_forcefield $solute_forcefield \
#                                               --solvent_forcefield $solvent_forcefield \
#                                               --outfile $outfile \

### COMPUTING ENERGIES IN VACCUUM ###

solvent_forcefield="amber14/tip4pd_desres.xml"
outfile="${PROJECT_PATH}/${pdb}/data/${pdb}_rosetta_nosol_energies.npy"

python -u ../src/eval_ff.py --rad 0 \
                            --sel 'resname [GACU]' \
                            --top $fixed_top \
                            --traj $fixed_traj \
                            --solute_ff $solute_forcefield \
                            --solvent_ff $solvent_forcefield \
                            --outfile $outfile \
