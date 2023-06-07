#!/usr/bin/env python

import argparse
from openmm.app import PDBFile
from openmm.unit import *
from openmm.app import StateDataReporter, CheckpointReporter
from mdtraj.reporters import XTCReporter

from simulation import NPTSimulator, NVTSimulator, load_config, replace_wildcards, add_args
from traj_tools import TrajFixer

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
master_config = add_args(master_config, simtype='equil')

minim_equil_steps = 0 # unstable for RNA in vaccuum
minim_equil_dt = 0.0005

NVT_equil_1_steps = 5000
NVT_equil_1_dt = 0.0001

NVT_equil_2_steps = 5000
NVT_equil_2_dt = 0.001

sampling_steps = int(master_config.sampling_freq / master_config.timestep)
simulation_steps = int(master_config.simulation_length / master_config.timestep)

time_elapsed = float(minim_equil_steps*minim_equil_dt + \
                     NVT_equil_1_steps*NVT_equil_1_dt + \
                     NVT_equil_2_steps*NVT_equil_2_dt)

total_time = float(master_config.simulation_length)
NPT_steps = int((total_time - time_elapsed)/master_config.timestep)

print(f"seed_path {master_config.seed_path}")
TF = TrajFixer(master_config.seed_path, master_config.seed_path)
fixed_pdb, _ = TF.fix_traj()

# performing energy minimization w/o solvent
minimizer = NVTSimulator(master_config.solute_ff, master_config.solvent_ff)
minimizer.modeller_from_MDtraj(fixed_pdb)
minimizer.prepare_minimization(temperature=sim_config.temperature*kelvin,
                               dt=minim_equil_dt*picoseconds)
#minimizer.minimize(maxIterations=10)
#minimizer.simulate(minim_equil_steps)
minimizer.write_state_to_pdb(master_config.nosol_path)
print("Minimization complete")

# performing NVT equilibration w/ solvent and small timestep
NVT_equilibrator_1 = NVTSimulator(master_config.solute_ff, master_config.solvent_ff)
NVT_equilibrator_1.transfer_modeller(minimizer)
NVT_equilibrator_1.prepare_equilibration(temperature=sim_config.temperature*kelvin,
                                         dt=NVT_equil_1_dt*picoseconds)
NVT_equilibrator_1.simulate(NVT_equil_1_steps)
print("NVT equilibration 1 complete")

# performing NVT equilibration w/ solvent and longer timestep
NVT_equilibrator_2 = NVTSimulator(master_config.solute_ff, master_config.solvent_ff)
NVT_equilibrator_2.transfer_simulation(NVT_equilibrator_1,
                                       temperature=sim_config.temperature*kelvin,
                                       dt=NVT_equil_2_dt*picosecond)
NVT_equilibrator_2.simulate(NVT_equil_2_steps)
NVT_equilibrator_2.write_state_to_pdb(master_config.sol_path)
print("NVT equilibration 2 complete")

# performing NPT equilibration w/ solvent
NPT_equilibrator = NPTSimulator(master_config.solute_ff, master_config.solvent_ff)
NPT_equilibrator.transfer_simulation(NVT_equilibrator_1,
                                     temperature=sim_config.temperature*kelvin,
                                     pressure=1*bar,
                                     dt=master_config.timestep*picoseconds)

log = StateDataReporter(master_config.log_path, master_config.sampling_freq, step=True, time=True,
                        speed=True, remainingTime=True, totalSteps=NPT_steps, separator='\t')
NPT_equilibrator.init_reporters(log)

NPT_equilibrator.simulate(NPT_steps)
NPT_equilibrator.save_state(master_config.state_path)
print("NPT equilibration complete")
