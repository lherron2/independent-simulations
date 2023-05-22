#!/bin/bash
#SBATCH -t 02:00:00
#SBATCH --ntasks-per-node=8
#SBATCH --mem-per-cpu=10240
#SBATCH --job-name=p_traj
#SBATCH --mail-type=NONE    # Send email at begin and end of job
#SBATCH --output=outfiles/postprocess_sim.out

DOCSTRING=$"""
Postprocesses simulations by computing relevant quantities (base-pairs, g-vectors, r-vectors, etc.)\n
\n
Args:\n
--pdb: The pdb ID of the structure (or some other identifier).\n
--iter: The 'round' of simulations being performed.\n
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

echo $pdb

root_path="${PROJECT_PATH}/${pdb}/${pdb}_iter${iter}"
topology="${root_path}/${pdb}_nosol.pdb"
master_config="${root_path}/master_prod.yaml"
data_path="${PROJECT_PATH}/${pdb}/data/"

cp "${root_path}/struct0/${pdb}_struct0_nosol.pdb" "${root_path}/${pdb}_nosol.pdb"

python -u ${SRCPATH}/postprocess_simulations.py --root_path $root_path \
                                                 --data_path $data_path \
                                                 --topology $topology \
                                                 --master_config $master_config \
