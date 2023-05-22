#!/bin/bash
#SBATCH -t 06:00:00
#SBATCH --ntasks-per-node=32
#SBATCH --mem-per-cpu=10240
#SBATCH --job-name=p_diff
#SBATCH --mail-type=NONE    # Send email at begin and end of job
#SBATCH --output=outfiles/postprocess_diff.out

DOCSTRING=$"""
Combines DDPM samples into a single file.\n
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

diffusion_path="/home/lherron/scratch/repos/thermodynamic-diffusion/systems/${pdb}/experiments/gvecs/10us/samples"
data_path="${PROJECT_PATH}/${pdb}/data"
subsample=1

python -u "${SRCPATH}/postprocess_diffusion.py" --pdbid $pdb \
                                                --diffusion_path $diffusion_path \
                                                --subsample $subsample \
                                                --data_path $data_path \

