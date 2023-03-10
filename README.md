# independent-simulations

Install openmm environment with: 
```
# create conda environment for openmm
conda env create -f openmm.yaml
```

Configure ```*.yaml``` for your systems.

Distribute ```.yaml``` files to your simulation directories with ```prep_sim_yaml.py --f sim_equil.yaml --structid 0 --temperatures temperatures.npy```.

Then run simulations with ```submit_run_equil_CUDA.sh```
