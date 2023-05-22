#!/bin/bash
#SBATCH -t 16:00:00
#SBATCH --ntasks-per-node=1
#SBATCH --job-name=p_rosetta
#SBATCH --mail-type=NONE    # Send email at begin and end of job
#SBATCH --output=outfiles/postprocess_rosetta.out

DOCSTRING=$"""
Postprocesses the Rosetta outputs by computing energies and the number of base pairs per structure.\n
\n
Args:\n
--pdb: The pdb ID of the structure (or some other identifier).\n
"""

POSITIONAL_ARGS=()

while [[ $# -gt 0 ]]; do
  case $1 in
    -h|--help)
      echo -e $DOCSTRING
      exit 1
      ;;
    --pdb)
      pdb="$2"
      shift
      shift
      ;;
    -*|--*)
      echo "Unknown option $1"
      exit 1
      ;;
    *)
      POSITIONAL_ARGS+=("$1") # save positional arg
      shift # past argument
      ;;
  esac
done

set -- "${POSITIONAL_ARGS[@]}" # restore positional parameters

source $HOME/.bashrc
source ../sourceme.sh
conda activate analysis


### FIXING BROKEN ROSETTA TRAJECTORIES ###

# edit these:
broken_traj="${PROJECT_PATH}/${pdb}/rosetta/${pdb}.xtc"
broken_top="${PROJECT_PATH}/${pdb}/rosetta/${pdb}_top.pdb"


# do not edit these:
fixed_traj="${PROJECT_PATH}/${pdb}/rosetta/${pdb}_fixed.xtc"
fixed_top="${PROJECT_PATH}/${pdb}/rosetta/${pdb}_top_fixed.pdb"

python -u "${SRCPATH}/fix_traj.py" --broken_traj $broken_traj \
                                   --broken_top $broken_top \
                                   --fixed_traj $fixed_traj \
                                   --fixed_top $fixed_top \

### COMPUTING GVECS FOR FIXED TRAJECTORIES ###

mkdir -p "${PROJECT_PATH}/${pdb}/data"
gvec_file="${PROJECT_PATH}/${pdb}/data/${pdb}_rosetta_gvecs.npy"

#python -u "${SRCPATH}/compute_gvecs.py" --traj $fixed_traj \
#                                        --top $fixed_top \
#                                        --outfile $gvec_file \

### COMPUTING ANNOTATIONS FOR FIXED TRAJECTORIES ###

annot_file="${PROJECT_PATH}/${pdb}/data/${pdb}_rosetta_annot.npy"

python -u "${SRCPATH}/annotate_traj.py" --traj $fixed_traj \
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
energy_file="${PROJECT_PATH}/${pdb}/data/${pdb}_rosetta_nosol_energies.npy"

python -u "${SRCPATH}/eval_ff.py" --rad 0 \
                                  --sel 'resname [GACU]' \
                                  --top $fixed_top \
                                  --traj $fixed_traj \
                                  --solute_ff $solute_forcefield \
                                  --solvent_ff $solvent_forcefield \
                                  --outfile $energy_file \
