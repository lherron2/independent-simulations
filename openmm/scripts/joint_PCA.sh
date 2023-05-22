#!/bin/bash
#SBATCH -t 00:30:00
#SBATCH --ntasks-per-node=24
#SBATCH --mem-per-cpu=10240
#SBATCH --job-name=pca
#SBATCH --mail-type=NONE    # Send email at begin and end of job
#SBATCH --output=outfiles/pca.out


DOCSTRING=$"""
Projects the MD data and DDPM data into a shared space: The first two
principal components of the MD data.\n
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

data_path="${PROJECT_PATH}/${pdb}/data"

python -u "${SRCPATH}/joint_PCA.py" --pdbid $pdb \
                                    --data_path $data_path
