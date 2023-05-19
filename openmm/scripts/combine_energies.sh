#!/bin/bash
#SBATCH -t 00:10:00
#SBATCH --ntasks-per-node=1
#SBATCH --job-name=combine
#SBATCH --mail-type=NONE    # Send email at begin and end of job
#SBATCH --output=combine.out

source $HOME/.bashrc
source ../sourceme.sh
# sourceme contains $CONDA and $PROJECT_PATH
#. "${CONDA_PREFIX_1}/etc/profile.d/conda.sh"
conda activate analysis

# INPUTS
pdb=$1
parameter="temperature"
replica_path="${PROJECT_PATH}/${pdb}/${pdb}_iter0/"
out_path="${PROJECT_PATH}/${pdb}/data/"
master_config="${replica_path}/master_prod.yaml"
file_identifier="r=$2_energies"
outfile="${pdb}_${file_identifier}"

python -u ../src/combine_files.py --pdbid $pdb \
                                --root_path $replica_path \
                                --master_config $master_config \
                                --file_identifier $file_identifier \
                                --out_path $out_path \
                                --outfile $outfile \

