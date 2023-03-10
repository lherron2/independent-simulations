# independent-simulations

## INSTALL
Install the openmm environment with: 
```
# create conda environment for openmm
conda env create -f openmm.yaml
```

Patch DESRES RNA force field files into conda openmm install via:
```
cp openmm/force_fields/* {CONDA_PATH}/envs/openmm/lib/python3.10/site-packages/openmm/app/data/amber14/
```
Your conda path can be found by running ```conda init```.

## CONVENTIONS

The simulation directories should be enumerated as ```structure{i}/``` and contain a file names as ```{pdbid}_structure{i}.pdb```. Paths can be configured as needed for the ```scripts/``` directory and in the ```config/```.

## USAGE

Simulations are parameterized by four files: ```master_equil.yaml``` and ```master_prod.yaml```, and  ```sim_equil.yaml``` and ```sim_prod.yaml```. The ```master.yaml``` files contain parameters which are shared across independent simulations, while the ```sim.yaml``` files contain parameters which are unique to a particular simulation (e.g. temperature).

To run simulations configure the ```*.yaml``` files for your system. Then distribute the ```*.yaml``` files to your simulation directories with ```prep_sim_yaml.py --f sim_equil.yaml --structid 0 --temperatures temperatures.npy```.

Then run simulations with either ```submit_run_equil_CUDA.sh``` and ```submit_run_prod_CUDA.sh```, editing the contents of the files to run on your HPC cluster.

