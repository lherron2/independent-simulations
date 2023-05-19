#!/bin/bash
#SBATCH -t 00:10:00
#SBATCH --ntasks-per-node=1
#SBATCH --job-name=gen_seeds
#SBATCH --mail-type=NONE    # Send email at begin and end of job
#SBATCH --output=outfiles/gen_seeds.out

source $HOME/.bashrc
source ../sourceme.sh
# sourceme contains $CONDA and $PROJECT_PATH
#. "$CONDA/etc/profile.d/conda.sh"
conda activate analysis

pdb=$1
iter=0
output_dir="${PROJECT_PATH}/${pdb}/${pdb}_iter${iter}"

# filenames from postprocess_rosetta.out
traj="${PROJECT_PATH}/${pdb}/rosetta/${pdb}_fixed.xtc"
top="${PROJECT_PATH}/${pdb}/rosetta/${pdb}_top_fixed.pdb"
energy_file="${PROJECT_PATH}/${pdb}/data/${pdb}_rosetta_nosol_energies.npy"
annot_file="${PROJECT_PATH}/${pdb}/data/${pdb}_rosetta_annot.npy"
num_structs=50

python -u ../src/gen_seeds.py --pdbid $pdb \
                              --traj $traj \
                              --top $top \
                              --energy_file $energy_file \
                              --annot_file $annot_file \
                              --output_dir $output_dir \
                              --num_structs $num_structs \
