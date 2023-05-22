#!/bin/bash
#SBATCH -t 02:00:00
#SBATCH --ntasks-per-node=2
#SBATCH --mem-per-cpu=10240
#SBATCH --job-name=nosol
#SBATCH --mail-type=NONE    # Send email at begin and end of job
#SBATCH --output=outfiles/trjcat.out

DOCSTRING=$"""
Concatenates simulation trajectories.\n
\n
Args:\n
--pdb: The pdb ID of the structure (or some other identifier).\n
--iter: The 'round' of simulations being performed.\n
--structid: The index of the simulation.\n
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

master_config="${PROJECT_PATH}/${pdb}/${pdb}_iter${iter}/master_prod.yaml" 
sim_config="${PROJECT_PATH}/${pdb}/${pdb}_iter${iter}/struct${structid}/sim_prod.yaml"

# change according to your file system
subsample=10

python -u ${SRCPATH}/trjcat.py --master_config $master_config \
                               --sim_config $sim_config \
                               --subsample $subsample \
                               --chunk_size 1 \
                               --desolvate False \

