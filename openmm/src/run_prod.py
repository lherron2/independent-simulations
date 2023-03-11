#!/usr/bin/env python

from openmm.app import *
from openmm import *
from openmm.unit import *
from openmmplumed import PlumedForce
from mdtraj.reporters import XTCReporter
import os
import yaml
import argparse

def load_yaml(file):
    with open(file, 'r') as stream:
            yaml_loaded = yaml.safe_load(stream)
    return yaml_loaded

def load_plumed_file(plumed_path, data_path, sampling_freq):
    """
    Currently unused but may be used in the future.
    """
    with open(plumed_path, 'r') as f:
        plumed_str = f.read()
    os.makedirs(os.path.join(data_path, f"colvar"), exist_ok=True)
    torsion_path = os.path.join(data_path, f"colvar/structure{structid}.torsions.colvar")
    plumed_str = plumed_str.replace("COLVARPATH", torsion_path).replace("COLVARSTRIDE", str(sampling_freq))
    return plumed_str

parser = argparse.ArgumentParser()
parser.add_argument('--master_yaml', required=True, 
                    type=str, help="master yaml file is required")
parser.add_argument('--sim_yaml', required=True, 
                    type=str, help="simulation specific yaml file is required")
args = parser.parse_args()

master_prod_params = load_yaml(args.master_yaml)
prod_params = load_yaml(args.sim_yaml)

temperature = int(prod_params["temperature"])
pdbid = master_prod_params["pdbid"]
structid = int(prod_params["structid"])
resume = master_prod_params["resume"]
sampling_freq = int(master_prod_params["sampling_freq"])
timestep = float(master_prod_params["timestep"])
simulation_length = int(master_prod_params["simulation_length"])
data_path = master_prod_params["data_path"]

data_path = data_path.replace("PDBID", pdbid).replace("STRUCTID", str(structid))

sampling_steps = int(sampling_freq / timestep)
total_steps = int(simulation_length / timestep)

pdb = PDBFile(os.path.join(data_path, f'{pdbid}_struct{structid}_sol.pdb'))
forcefield = ForceField('amber14/RNA.Shaw_charmm22-ions.xml', 'amber14/tip4pd_desres.xml')
#pdb.topology.setUnitCellDimensions(Vec3(box_dim, box_dim, box_dim)*nanometers)
system = forcefield.createSystem(pdb.topology, nonbondedMethod=PME,
        nonbondedCutoff=1*nanometer, constraints=HBonds)

system.addForce(MonteCarloBarostat(1*bar, temperature*kelvin))
system.addForce(AndersenThermostat(temperature*kelvin, 1/picosecond))

integrator = LangevinMiddleIntegrator(temperature*kelvin, 1/picosecond, timestep*picoseconds)
simulation = Simulation(pdb.topology, system, integrator)

if not resume:
    simulation.loadCheckpoint(os.path.join(data_path, f'{pdbid}_struct{structid}_equil.chk'))
    remaining_steps = total_steps
else:
    simulation.loadCheckpoint(os.path.join(data_path, f'{pdbid}_struct{structid}.chk'))
    steps_simulated = np.loadtxt(os.path.join(data_path, f'{pdbid}_struct{structid}.energy'), 
                                 skiprows=1, delimiter=',')[-1][0]
    remaining_steps = total_steps - steps_simulated

simulation.reporters.append(XTCReporter(os.path.join(data_path, f'{pdbid}_struct{structid}.xtc'), 
                                        sampling_steps, append=resume))
simulation.reporters.append(StateDataReporter(os.path.join(data_path, f'{pdbid}_struct{structid}.energy'), 
                                              sampling_steps, step=True, potentialEnergy=True, temperature=True, 
                                              append=resume))
simulation.reporters.append(StateDataReporter(os.path.join(data_path, f'{pdbid}_struct{structid}.log'), sampling_steps, 
                                              step=True, time=True, speed=True, remainingTime=True, append=resume, 
                                              totalSteps=total_steps, separator='\t'))
simulation.reporters.append(CheckpointReporter(os.path.join(data_path, f'{pdbid}_struct{structid}.chk'), sampling_steps))

simulation.step(remaining_steps)
