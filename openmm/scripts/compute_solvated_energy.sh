#!/bin/bash
#SBATCH -t 16:00:00
#SBATCH --ntasks-per-node=1
#SBATCH --job-name=energies
#SBATCH --mail-type=NONE    # Send email at begin and end of job
#SBATCH --output=energies.out


DOCSTRING=$"""
Evaluates the forcefield over a solvated trajectory to compute energies.\n
\n
Args:\n
--pdb: The pdb ID of the structure (or some other identifier).\n
--iter: The 'round' of simulations being performed.\n
--structid: The index of the simulation.\n
--rad: Cutoff radius of the solvation shell.\n
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
    --iter)
      iter="$2"
      shift
      shift
      ;;
    --structid)
      structid=$2
      shift
      shift
      ;;
    --rad)
      rad=$2
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

source $HOME/.bashrc
source ../sourceme.sh
conda activate analysis

# INPUTS
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

