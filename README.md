# independent-simulations

## INSTALL
Install the openmm environment with: 
```
cd openmm
# create conda environment for openmm
conda env create -f analysis.yaml
```

Patch DESRES RNA force field files into conda openmm install via:
```
conda activate analysis
cp ff/* $CONDA_PREFIX/lib/python3.10/site-packages/openmm/app/data/amber14/
```

Initialize the `sourceme.sh` file by running `./configure.sh`. This will set the `$PROJECT_PATH` variable to be `openmm/experiments`. This path can be changed manually by the user.

## USAGE

Currently this tutorial assumes that the Rosetta outputs for your RNA sequence are located in `$PROJECT_PATH/$PDB/rosetta` as a `.xtc` trajectory file and a `.pdb` topology file. In the future the documentation will be updated to include generating an ensemble of initial structures using Rosetta.

The structures produced by Rosetta will likely be missing atoms required by the forcefield, and to choose reasonable initial conditions to being simulations from we need to evaluate the forcefield for each structure along with the number of well-formed base pairs. To do this run `postprocess_rosetta.sh`, which will fix the rosetta outputs and write energy (`$PDB_rosetta_nosol_energies.npy`) and base-pair (`$PDB_rosetta_annot.npy`) files into `$PROJECT_PATH/$PDB/data/`.

Now, to generate starting structures, run 
```gen_seeds.sh --pdb $PDB --iter 0 --num_structs $N --min-temp $min_T --max-temp $max_T```, which will create a directory `$PDB_iter0/` in `$PROJECT_PATH/$PDB/rosetta` containing `$N` initial starting structures, with temperatures evenly spaced between `$min_T` and `$max_T`. The second argument is the simualtion iteration which can be modified if multiple rounds of simulation are performed.

Simulations are parameterized by four files: ```master_equil.yaml``` and ```master_prod.yaml```, and  ```sim_equil.yaml``` and ```sim_prod.yaml```. The ```master*.yaml``` files contain parameters which are shared across the independent simulations, while the ```sim*.yaml``` files contain parameters which are unique to a particular simulation (e.g. temperature). Edit these files to change things such as the integration timestep or the simulation length.

Then equilibrate your system with
```
for i in {0..$N}; do
  sbatch run_equil.sh --pdb $PDB --structid $i;
done
``` 
and then run a production simulation with
```
for sim_idx in {0..$N}; do
  sbatch run_prod.sh --pdb $PDB --structid $i;
done
```
where `$i` refers to the index of a simulation directory setup by `gen_seeds.sh`. For `run_prod.sh`, to resume simulations set the `resume` variable in `master_prod.yaml` to `True`. Make sure `resume = False` if starting from scratch. 

Pro tip for clusters that have a scavenger partition:

To optimize resource allocation, you can follow these steps:

1. In the first round of simulations, set them to run in the GPU partition for a very short amount of time. Make sure the duration is greater than the sampling frequency so that a checkpoint is created.

2. Once the short simulations have finished, set `resume = True`.

3. Re-submit the jobs to the scavenger partition.

By doing this, the simulations will run when the cluster is underutilized, allowing for more high-priority simulations to take precedence. This approach helps optimize the usage of available resources on the cluster.

Once the simulation are complete, run 
```
for i in {0..$N}; do
  remove_solvent.sh --pdb $PDB --structid $i;
done
```
and
```
for sim_idx in {0..$N}; do
  trjcat.sh --pdb $PDB --structid $i;
done
```

There are two important steps to prepare the simulation data:

1. Remove solvent from the `xtc` files generated during the simulation. This can be done using the former method.

2. Concatenate all the `xtc` files together to form a continuous trajectory. This step is essential for creating the diffusion dataset and conducting subsequent analysis.

After completing these steps, you can proceed with the following:

- Run the `postprocess_simulations.py` script with the parameter `--pdb $PDB` to compute relevant quantities for the simulation. One of these quantities is the G vectors, as defined in XXX. These G vectors will be used to create a dataset for training a diffusion model.

- To create the dataset, execute the `rvec_to_dataset.sh $PDB` script. It will write the dataset to the `$PROJECT_PATH/$PDB/data/` directory.

## EXAMPLE

The provided example located in `openmm/experiments/` will run five simulations of a GCAA tetraloop RNA (pdbid: 1zih) at temperatures between 310K and 410K.

First we have to activate the conda environment and add the correct pathing by running:
```
cd openmm
./configure.sh
cd scripts
```

To run the provided example execute:
```
# fixing rosetta outputs and computing clustering quantities
sbatch postprocess_rosetta.sh --pdb 1zih;

# selecting starting seeds based on clustering and assigning files and temperatures
sbatch gen_seeds.sh --pdb 1zih --iter 0 --num-structs 5 --min-temp 310 --max-temp 410;

# running equilibration from master_equil.yaml
for i in {0..4}; do
  sbatch run_equil.sh --pdb 1zih --iter 0 --structid $i;
done

# running production from master_equil.yaml
for i in {0..4}; do
  sbatch run_prod.sh --pdb 1zih --iter 0 --structid $i;
done

```

Once the simulations are done running, postprocess them by running:
```
# concatenating production trajectories and removing solvent
for i in {0..4}; do
  sbatch remove_solvent.sh --pdb 1zih ---iter 0 -structid $i;
done

# concatenating production trajectories while keeping solvent
for i in {0..4}; do
  sbatch trjcat.sh --pdb 1zih --iter 0 --structid $i;
done

# computing relevent quantities from desolvated trajectory
sbatch postprocess_traj.sh --pdb 1zih

# creating dataset for diffusion model
sbatch gvec_to_dataset.sh --pdb 1zih

# computing energy w/ 2.5A solvation shell from solvated trajectory
for i in {0..4}; do
  sbatch compute_solvated_energy --pdb 1zih --structid $i --rad 2.5
done

sbatch combine_energies.sh --pdb 1zih --iter 0 --rad 2.5
```

Note that the submission scripts are configured to request GPU nodes from UMD's HPC computing cluster. You may have to edit the script to be request the correct resources from your HPC cluster. If `sbatch` is not available `bash` can be used instead.

