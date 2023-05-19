#!/bin/bash
#SBATCH -t 00:10:00
#SBATCH --ntasks-per-node=1
#SBATCH --job-name=gen_seeds
#SBATCH --mail-type=NONE
#SBATCH --output=outfiles/gen_seeds.out

source $HOME/.bashrc
source ../sourceme.sh
# sourceme contains $CONDA and $PROJECT_PATH
#. "$CONDA/etc/profile.d/conda.sh"
conda activate analysis

pdb=$1
iter=$2
num_structs=$3
min_temp=$4
max_temp=$5
output_dir="${PROJECT_PATH}/${pdb}/${pdb}_iter${iter}"

# filenames from postprocess_rosetta.out
traj="${PROJECT_PATH}/${pdb}/rosetta/${pdb}_fixed.xtc"
top="${PROJECT_PATH}/${pdb}/rosetta/${pdb}_top_fixed.pdb"
energy_file="${PROJECT_PATH}/${pdb}/data/${pdb}_rosetta_nosol_energies.npy"
annot_file="${PROJECT_PATH}/${pdb}/data/${pdb}_rosetta_annot.npy"

mkdir -p $output_dir
cp "${REPOROOT}/templates/config_templates/"* $output_dir
sed -i "s+PDBID+$pdb+g" "${output_dir}/master_equil.yaml"
sed -i "s+PDBID+$pdb+g" "${output_dir}/master_prod.yaml"

python -u ../src/gen_seeds.py --pdbid $pdb \
                              --traj $traj \
                              --top $top \
                              --energy_file $energy_file \
                              --annot_file $annot_file \
                              --output_dir $output_dir \
                              --num_structs $num_structs \

python -u ../src/gen_temps.py --min_temp $min_temp \
                              --max_temp $max_temp \
                              --num_structs $num_structs \
                              --output_dir $output_dir \

for i in $(seq $num_structs); do
    echo $i
    cp "${output_dir}/sim_equil.yaml" "${output_dir}/struct${i}/sim_equil.yaml"
    cp "${output_dir}/sim_prod.yaml" "${output_dir}/struct${i}/sim_prod.yaml"

    python -u ../src/prep_sim_yaml.py --yaml "${output_dir}/sim_equil.yaml" \
                                      --sim_dir "${output_dir}/struct${i}" \
                                      --structid $i \
                                      --temperatures "${output_dir}/temperatures.npy"

    python -u ../src/prep_sim_yaml.py --yaml "${output_dir}/sim_prod.yaml" \
                                      --sim_dir "${output_dir}/struct${i}" \
                                      --structid $i \
                                      --temperatures "${output_dir}/temperatures.npy" 
done
