#!/bin/bash
#SBATCH -t 00:10:00
#SBATCH --ntasks-per-node=1
#SBATCH --job-name=combine
#SBATCH --mail-type=NONE    # Send email at begin and end of job
#SBATCH --output=combine.out

DOCSTRING=$"""
Combines energy files across simulation indices into a single file.\n
\n
Args:\n
--pdb: The pdb ID of the structure (or some other identifier).\n
--iter: The 'round' of simulations being performed.\n
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
      pdb="$2"
      shift
      shift
      ;;
    --rad)
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

# INPUTS
parameter="temperature"
replica_path="${PROJECT_PATH}/${pdb}/${pdb}_iter${iter}/"
out_path="${PROJECT_PATH}/${pdb}/data/"
master_config="${replica_path}/master_prod.yaml"
file_identifier="r=${rad}_energies"
outfile="${pdb}_${file_identifier}"

python -u "${SRCPATH}/combine_files.py" --pdbid $pdb \
                                        --root_path $replica_path \
                                        --master_config $master_config \
                                        --file_identifier $file_identifier \
                                        --out_path $out_path \
                                        --outfile $outfile \

