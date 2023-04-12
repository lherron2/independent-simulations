#!/usr/bin/env python

from openmm.app import *
from openmm import *
from openmm.unit import *
from mdtraj.reporters import XTCReporter
import os
import yaml
import argparse
import numpy as np
import subprocess

def load_yaml(file):
    with open(file, 'r') as stream:
            yaml_loaded = yaml.safe_load(stream)
    return yaml_loaded

def bash(command):
    "submits a command to the terminal. Particularly useful for text manipulation commands"
    output = subprocess.check_output(command, shell=True).decode("utf-8").rstrip().split("\n")
    return output

def get_simulation_idx(data_path, pdbid, structid, identifier):
    xtc_string=f"{pdbid}_{identifier}{structid}_"
    xtc_list = bash(f"ls {data_path} | grep '{xtc_string}[0-9]*\.xtc'")
    simulation_indices = np.array([int(i.split(xtc_string)[-1].split('.xtc')[0]]) for i in xtc_list])
    simulation_index = max(simulation_indices) + 1
    return simulation_index

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
identifier = master_prod_params["identifier"]
resume = master_prod_params["resume"]
sampling_freq = int(master_prod_params["sampling_freq"])
timestep = float(master_prod_params["timestep"])
simulation_length = int(master_prod_params["simulation_length"])
data_path = master_prod_params["data_path"]

data_path = data_path.replace("PDBID", pdbid).replace("STRUCTID", str(structid))

sampling_steps = int(sampling_freq / timestep)
total_steps = int(simulation_length / timestep)

pdb = PDBFile(os.path.join(data_path, f'{pdbid}_{identifier}{structid}_sol.pdb'))
forcefield = ForceField('amber14/RNA.Shaw_charmm22-ions.xml', 'amber14/tip4pd_desres.xml')
#pdb.topology.setUnitCellDimensions(Vec3(box_dim, box_dim, box_dim)*nanometers)
system = forcefield.createSystem(pdb.topology, nonbondedMethod=PME,
        nonbondedCutoff=1*nanometer, constraints=HBonds)

system.addForce(MonteCarloBarostat(1*bar, temperature*kelvin))
system.addForce(AndersenThermostat(temperature*kelvin, 1/picosecond))

integrator = LangevinMiddleIntegrator(temperature*kelvin, 1/picosecond, timestep*picoseconds)
simulation = Simulation(pdb.topology, system, integrator)

if not resume:
    simulation_idx = 0
    simulation.loadCheckpoint(os.path.join(data_path, f'{pdbid}_{identifier}{structid}_equil.chk'))
    remaining_steps = total_steps
else:
    simulation_idx = get_simulation_idx(data_path, pdbid, structid, identifier)
    simulation.loadCheckpoint(os.path.join(data_path, f'{pdbid}_{identifier}{structid}.chk'))
    steps_simulated = int(bash(f"tail -1 {os.path.join(data_path, f'{pdbid}_{identifier}{structid}.energy')}")[0].split(',')[0])
    remaining_steps = total_steps - steps_simulated

simulation.reporters.append(XTCReporter(os.path.join(data_path, f'{pdbid}_{identifier}{structid}_{simulation_idx}.xtc'),
                                        sampling_steps, append=False))
simulation.reporters.append(StateDataReporter(os.path.join(data_path, f'{pdbid}_{identifier}{structid}.energy'),
                                              sampling_steps, step=True, potentialEnergy=True, temperature=True,
                                              append=resume))
simulation.reporters.append(StateDataReporter(os.path.join(data_path, f'{pdbid}_{identifier}{structid}.log'), sampling_steps,
                                              step=True, time=True, speed=True, remainingTime=True, append=resume,
                                              totalSteps=total_steps, separator='\t'))
simulation.reporters.append(CheckpointReporter(os.path.join(data_path, f'{pdbid}_{identifier}{structid}.chk'), sampling_steps))

simulation.step(remaining_steps)
