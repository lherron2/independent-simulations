#!/usr/bin/env python

import argparse
import subprocess
import os
import numpy as np

from openmm.app import PDBFile
from openmm.unit import *
from openmm.app import StateDataReporter, CheckpointReporter
from mdtraj.reporters import XTCReporter

from simulation import NPTSimulator, NVTSimulator, load_config, replace_wildcards, add_args
from traj_tools import TrajFixer

def bash(command):
    "submits a command to the terminal. Particularly useful for text manipulation commands"
    output = subprocess.check_output(command, shell=True).decode("utf-8").rstrip().split("\n")
    return output

def get_simulation_idx(data_path, pdbid, structid, identifier):
    xtc_string=f"{pdbid}_{identifier}{structid}_"
    xtc_list = bash(f"ls {'/'.join(data_path.split('/')[:-1])} | grep '{xtc_string}[0-9]*\.xtc'")
    simulation_indices = np.array([int(i.split(xtc_string)[-1].split('.xtc')[0]) for i in xtc_list])
    simulation_index = max(simulation_indices) + 1
    return simulation_index


parser = argparse.ArgumentParser()
parser.add_argument('--master_config',
                    required=True,
                    type=str)
parser.add_argument('--sim_config',
                    required=True,
                    type=str)
args = parser.parse_args()

master_config = load_config(args.master_config)
sim_config = load_config(args.sim_config)
master_config = replace_wildcards(master_config, sim_config)
master_config = add_args(master_config, simtype='prod')

total_steps = int(master_config.simulation_length/master_config.timestep)
sampling_freq = int(master_config.sampling_freq/master_config.timestep)

#initializing simulation
NPT_production =  NPTSimulator(master_config.solute_ff, master_config.solvent_ff)
NPT_production.extract_top_pos(PDBFile(master_config.sol_path))
NPT_production.init_simulation(temperature=sim_config.temperature*kelvin,
                               pressure=1*bar,
                               dt=master_config.timestep*picoseconds)

print("Simulation Initialized")

# resuming from checkpoint
if not master_config.resume:
    simulation_idx = 0
    NPT_production.simulation_from_state(master_config.state_path)
    master_config.xtc_path = os.path.join('/'.join(master_config.seed_path.split('/')[:-1]),
            f'{master_config.pdbid}_{master_config.identifier}{sim_config.structid}_{0}.xtc')
    remaining_steps = total_steps
else:
    simulation_idx = get_simulation_idx(master_config.root_path,
                                        master_config.pdbid,
                                        sim_config.structid,
                                        master_config.identifier)
    NPT_production.simulation_from_checkpoint(master_config.chk_path)
    steps_simulated = int(bash(f"tail -1 {master_config.energy_path}")[0].split(',')[0])
    remaining_steps = total_steps - steps_simulated

master_config.xtc_path = os.path.join('/'.join(master_config.seed_path.split('/')[:-1]),
        f'{master_config.pdbid}_{master_config.identifier}{sim_config.structid}_{simulation_idx}.xtc')
print("Resuming from checkpoint ...")

# configuring reporters
xtc = XTCReporter(master_config.xtc_path, sampling_freq, append=False)
energy = StateDataReporter(master_config.energy_path, sampling_freq, step=True,
                           potentialEnergy=True, temperature=True, append=master_config.resume)
log = StateDataReporter(master_config.log_path, sampling_freq, step=True, time=True,
                        speed=True, remainingTime=True, append=master_config.resume,
                        totalSteps=master_config.simulation_length, separator='\t')
chk = CheckpointReporter(master_config.chk_path, sampling_freq)

print("Reporters Initialized ...")
NPT_production.init_reporters(xtc, energy, log, chk)

print("Simulation Beginning ...")
NPT_production.simulate(remaining_steps)
