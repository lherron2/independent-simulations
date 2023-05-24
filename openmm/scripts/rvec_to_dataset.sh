#!/bin/bash
#SBATCH -t 02:00:00
#SBATCH --ntasks-per-node=24
#SBATCH --mem-per-cpu=10240
#SBATCH --job-name=dataset
#SBATCH --mail-type=NONE    # Send email at begin and end of job
#SBATCH --output=outfiles/dataset.out

DOCSTRING=$"""
Creates a dataset from r-vectors for use with the thermodynamic-diffusion library.\n
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
# sourceme contains $CONDA and $PROJECT_PATH
#. "${CONDA_PREFIX_1}/etc/profile.d/conda.sh"
conda activate analysis

rvec_path="${PROJECT_PATH}/${pdb}/data/${pdb}_MD_rvecs.npy"
dataset_path="${PROJECT_PATH}/${pdb}/data/${pdb}_rvec_dataset.npy"

python -u "${SRCPATH}/rvec_to_dataset.py" --rvec_path $rvec_path \
                                          --dataset_path $dataset_path \
