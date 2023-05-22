#!/usr/bin/env bash
#SBATCH -t 02:00:00
#SBATCH --ntasks-per-node=1
#SBATCH --partition=gpu
#SBATCH --gpus=a100:1
#SBATCH --job-name=prod
#SBATCH --mail-type=NONE    # Send email at begin and end of job
#SBATCH --output=outfiles/prod.out

DOCSTRING=$"""
Runs a production NPT simulation of the system.\n
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

module purge
module load cuda

master_config="${PROJECT_PATH}/${pdb}/${pdb}_iter${iter}/master_prod.yaml"
sim_config="${PROJECT_PATH}/${pdb}/${pdb}_iter${iter}/struct${structid}/sim_prod.yaml"

"${SRCPATH}/simulate.py" --master_config $master_config \
                         --sim_config $sim_config \
