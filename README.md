# independent-simulations

## INSTALL
Install the openmm environment with: 
```
cd openmm
# create conda environment for openmm
conda env create -f openmm.yaml
```

Patch DESRES RNA force field files into conda openmm install via:
```
conda activate openmm
cp ff/* $CONDA_PREFIX/lib/python3.10/site-packages/openmm/app/data/amber14/
```

## CONVENTIONS

The simulation directories should be enumerated as ```structure{i}/``` and contain a file names as ```{pdbid}_structure{i}.pdb```. Paths can be configured as needed for the ```scripts/``` directory and in the ```config/```.

## USAGE

Simulations are parameterized by four files: ```master_equil.yaml``` and ```master_prod.yaml```, and  ```sim_equil.yaml``` and ```sim_prod.yaml```. The ```master.yaml``` files contain parameters which are shared across independent simulations, while the ```sim.yaml``` files contain parameters which are unique to a particular simulation (e.g. temperature).

To run simulations configure the ```*.yaml``` files for your system. Then distribute the ```*.yaml``` files to your simulation directories with ```prep_sim_yaml.py --f sim_equil.yaml --structid 0 --temperatures temperatures.npy```.

Then run simulations with either ```submit_run_equil_CUDA.sh``` and ```submit_run_prod_CUDA.sh```, editing the contents of the files to run on your HPC cluster.

## EXAMPLE

The provided example will run two simulations of HIV-TAR RNA structures (pdbid: 1anr) at 310K and 350K.

First we have to activate the conda environment and add the python scripts located in ```openmm/src``` to the system ```$PATH``` by running
```
conda activate openmm
cd openmm
source sourceme.sh
```

To run the provided example, first substitute the data path for your system into the master_prod.yaml and master_equil.yaml by executing:
```
cd example
sed -i "s+DATAPATH+$PWD/structSTRUCTID+g" "yaml/master_prod.yaml"
sed -i "s+DATAPATH+$PWD/structSTRUCTID+g" "yaml/master_equil.yaml"
```
and distribute the simulation-specific configuration files to the simulation directories via:
```
for i in {0..1}; do
	prep_sim_yaml.py --yaml yaml/sim_equil.yaml --structid $i --temperatures temperatures.npy
	prep_sim_yaml.py --yaml yaml/sim_prod.yaml --structid $i --temperatures temperatures.npy
done
```

Then submit the job to your HPC resources by executing:
```
cd ../scripts
for i in {0..1}; do
	sbatch submit_run_equil_CUDA.sh 1anr $i
done
```
Note that the submission scripts are configured to request GPU nodes from UMD's HPC computing cluster. You may have to edit the script to be request the correct resources from your HPC cluster. 

Once the equilibration finishes, run the production simulation by executing:
```
for i in {0..1}; do
	sbatch submit_run_equil_CUDA.sh 1anr $i
done
```

+ Change the ```examples/yaml``` directory to ```examples/config```.
