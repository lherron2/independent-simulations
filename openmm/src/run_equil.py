#!/usr/bin/env python

from openmm.app import *
from openmm import *
from openmm.unit import *
from mdtraj.reporters import XTCReporter
from scipy.spatial import distance_matrix
import os
import yaml
import argparse

def load_yaml(file):
    with open(file, 'r') as stream:
            yaml_loaded = yaml.safe_load(stream)
    return yaml_loaded

parser = argparse.ArgumentParser()
parser.add_argument('--master_yaml', required=True,
                    type=str, help="master yaml file is required")
parser.add_argument('--sim_yaml', required=True,
                    type=str, help="simulation specific yaml file is required")
args = parser.parse_args()

# loading yaml files
master_equil_params = load_yaml(args.master_yaml)
equil_params = load_yaml(args.sim_yaml)

# assigning parameters from yaml files
temperature = int(equil_params["temperature"])
pdbid = master_equil_params["pdbid"]
structid = int(equil_params["structid"])
identifier = master_equil_params["identifier"]
sampling_freq = int(master_equil_params["sampling_freq"])
timestep = float(master_equil_params["timestep"])
simulation_length = int(master_equil_params["simulation_length"])
data_path = master_equil_params["data_path"]

data_path = data_path.replace("PDBID", pdbid).replace("STRUCTID", str(structid))

sampling_steps = int(sampling_freq / timestep)
simulation_steps = int(simulation_length / timestep)

# preparing system
pdb = PDBFile(os.path.join(data_path, f'{pdbid}_{identifier}{structid}.pdb'))
forcefield = ForceField('amber14/RNA.Shaw_charmm22-ions.xml', 'amber14/tip4pd_desres.xml')
unminimized_modeller = Modeller(pdb.topology, pdb.positions)
unminimized_modeller.addExtraParticles(forcefield)

PDBFile.writeFile(unminimized_modeller.topology, unminimized_modeller.positions,
                  open(os.path.join(data_path, f'{pdbid}_{identifier}{structid}_nosol.pdb'), 'w'))

dmat = distance_matrix(unminimized_modeller.positions.value_in_unit(nanometers),
                        unminimized_modeller.positions.value_in_unit(nanometers))
box_dim = 3*max(1, dmat.std()) + dmat.max()

unminimized_modeller.addSolvent(forcefield, boxSize=Vec3(box_dim, box_dim, box_dim)*nanometers,
                    model='tip4pew')
unminimized_modeller.deleteWater()

system = forcefield.createSystem(unminimized_modeller.topology,
                                 nonbondedMethod=PME,
                                 nonbondedCutoff=1*nanometer,
                                 constraints=HBonds)

system.addForce(MonteCarloBarostat(1*bar, temperature*kelvin))
system.addForce(AndersenThermostat(temperature*kelvin, 1/picosecond))

integrator = LangevinMiddleIntegrator(temperature*kelvin, 1/picosecond, 0.0005*picoseconds)
minimizer = Simulation(unminimized_modeller.topology, system, integrator)
minimizer.context.setPositions(unminimized_modeller.positions)
minimizer.context.setVelocitiesToTemperature(temperature)
minimizer.minimizeEnergy()
minimized_positions = minimizer.context.getState(getPositions=True).getPositions()


minimized_modeller = Modeller(minimizer.topology, minimized_positions)
minimized_modeller.addSolvent(forcefield, boxSize=Vec3(box_dim, box_dim, box_dim)*nanometers,
                    ionicStrength=1*molar, positiveIon='K+', negativeIon='Cl-', model='tip4pew')


integrator = LangevinMiddleIntegrator(temperature*kelvin, 1/picosecond, 0.0005*picoseconds)
simulation = Simulation(minimizer.topology, system, integrator)
simulation.context.setPositions(minimized_positions)
simulation.context.setVelocitiesToTemperature(temperature)
simulation.minimizeEnergy()

PDBFile.writeFile(simulation.topology, simulation.context.getState(getPositions=True).getPositions(),
                  open(os.path.join(data_path, f'{pdbid}_{identifier}{structid}_sol.pdb'), 'w'))

simulation.step(1000)
integrator = LangevinMiddleIntegrator(temperature*kelvin, 1/picosecond, timestep*picoseconds)
simulation.reporters.append(XTCReporter(os.path.join(data_path,
                                                     f'{pdbid}_{identifier}{structid}_equil.xtc'), sampling_steps))
simulation.reporters.append(StateDataReporter(os.path.join(data_path, f'{pdbid}_{identifier}{structid}_equil.log'), sampling_steps,
                                              step=True, time=True, speed=True, remainingTime=True,
                                              totalSteps=simulation_steps, separator='\t'))
# running simulation
simulation.step(simulation_steps)
simulation.saveCheckpoint(os.path.join(data_path, f'{pdbid}_{identifier}{structid}_equil.chk'))
