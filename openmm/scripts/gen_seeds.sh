#!/bin/bash
#SBATCH -t 00:10:00
#SBATCH --ntasks-per-node=1
#SBATCH --job-name=gen_seeds
#SBATCH --mail-type=NONE
#SBATCH --output=outfiles/gen_seeds.out

DOCSTRING=$"""
Script which generates seeds for an RNA simulation based on clustering performed on the
Rosetta outputs. This script requires that the rosetta outputs are saved
as an xtc trajectory file and a pdb topology file. In this script the
names are expected to be \${pdb}_fixed.xtc and \${pdb}_fixed_top.pdb. The 'fixed' in 
the names is because the trajectory and topology are the outputs of postprocess_rosetta.sh\n
\n
Using these files the script will create a directory \${PROJECT_PATH}/\${pdb}/\${pdb}_iter\${iter} which contains
the simulation directories. For example, independent-simulations/openmm/experiments/1zih/1zih_iter0.\n
\n
Args:\n
--pdb: The pdb ID of the structure (or some other identifier).\n
--iter: The 'round' of simulations being performed.\n
--num-structs: The number of simulations to perform.\n
--min-temp: The minimum temperature to simulate.\n
--max-temp: The maximum temperature to simulate.\n
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
    --num-structs)
      num_structs=$2
      shift
      shift
      ;;
    --min-temp)
      min_temp=$2
      shift
      shift
      ;;
    --max-temp)
      max_temp=$2
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
#. "$CONDA/etc/profile.d/conda.sh"
conda activate analysis


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
sed -i "s+PROJECTPATH+$PROJECT_PATH+g" "${output_dir}/master_equil.yaml"
sed -i "s+PROJECTPATH+$PROJECT_PATH+g" "${output_dir}/master_prod.yaml"

python -u "${SRCPATH}/gen_seeds.py" --pdbid $pdb \
                                    --traj $traj \
                                    --top $top \
                                    --energy_file $energy_file \
                                    --annot_file $annot_file \
                                    --output_dir $output_dir \
                                    --num_structs $num_structs \

python -u "${SRCPATH}/gen_temps.py" --min_temp $min_temp \
                                    --max_temp $max_temp \
                                    --num_structs $num_structs \
                                    --output_dir $output_dir \

for i in $(seq 0 $(($num_structs-1))); do
    echo $i
    cp "${output_dir}/sim_equil.yaml" "${output_dir}/struct${i}/sim_equil.yaml"
    cp "${output_dir}/sim_prod.yaml" "${output_dir}/struct${i}/sim_prod.yaml"

    python -u "${SRCPATH}/prep_sim_yaml.py" --yaml "${output_dir}/sim_equil.yaml" \
                                            --sim_dir "${output_dir}/struct${i}" \
                                            --structid $i \
                                            --temperatures "${output_dir}/temperatures.npy"

    python -u "${SRCPATH}/prep_sim_yaml.py" --yaml "${output_dir}/sim_prod.yaml" \
                                            --sim_dir "${output_dir}/struct${i}" \
                                            --structid $i \
                                            --temperatures "${output_dir}/temperatures.npy" 
done
