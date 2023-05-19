import yaml
from types import SimpleNamespace
import numpy as np
import parmed as pmd
from openmm.app import Modeller, ForceField, Simulation, PDBFile, PDBxFile, PME, HBonds
from openmm.unit import *
from openmm import LangevinMiddleIntegrator, MonteCarloBarostat, AndersenThermostat, Vec3
import openmm
import pdbfixer
from openmm.app.internal.pdbstructure import PdbStructure
import io
from utils import *
from scipy.spatial import distance_matrix
import mdtraj

def load_config(file):
    with open(file, 'r') as stream:
            yaml_loaded = yaml.safe_load(stream)
    return SimpleNamespace(**yaml_loaded)

def replace_wildcards(master_namespace, sim_namespace):
    replaced_namespace = {}
    for k, v in master_namespace.__dict__.items():
        for kw, vw in sim_namespace.__dict__.items():
            if not isinstance(v, str):
                replaced_namespace[k] = v
            if isinstance(v, str):
                replaced_namespace[k] = v.replace(kw.upper(), str(vw))
        for kw, vw in master_namespace.__dict__.items():
            if isinstance(v, str):
                replaced_namespace[k] = replaced_namespace[k].replace(kw.upper(), str(vw))

    return SimpleNamespace(**replaced_namespace)

def add_args(master_namespace, simtype):
    root = master_namespace.seed_path.removesuffix('.pdb')
    master_namespace.root_path = root
    master_namespace.nosol_path = root + '_nosol.pdb'
    master_namespace.sol_path = root + '_sol.pdb'
    master_namespace.state_path = root + '_state.xml'

    if simtype == 'prod':
        master_namespace.energy_path = root + '.energy'
        master_namespace.log_path = root + '.log'
        master_namespace.chk_path = root + '.chk'
    if simtype == 'equil':
        master_namespace.log_path = root + '_equil.log'


    return master_namespace

def decomposeQuantity(quantity):
    return quantity.value_in_unit(quantity.unit), quantity.unit

class LightweightSimulator:
    def __init__(self, ff_solute, ff_solvent):
        self.forcefield = ForceField(ff_solute, ff_solvent)

    def spawn_simulation(self, topology, coordinates, unit=nanometer, implicit_solvent=False):
        modeller = Modeller(topology, coordinates*unit)
        modeller.addExtraParticles(self.forcefield)
        modeller.addHydrogens(self.forcefield)
        if implicit_solvent:
            subsystem = self.forcefield.createSystem(modeller.topology, implicitSolventKappa=2.35)
        else:
            subsystem = self.forcefield.createSystem(modeller.topology)
        integrator = LangevinMiddleIntegrator(310*kelvin, 1/picosecond, 0.0005*picoseconds)
        simulation = Simulation(modeller.topology,
                                subsystem,
                                integrator,
                                platform=openmm.Platform.getPlatformByName('CPU'))
        simulation.context.setPositions(modeller.positions)
        self.simulation = simulation
        return simulation

    def get_potential_energy(self, simulation, unit=openmm.unit.kilocalorie_per_mole):
        state = simulation.context.getState(getEnergy=True)
        pot = state.getPotentialEnergy() / unit
        return pot

class ModellerWrapper:
    def __init__(self, forcefield):
        self.modeller = None
        self.box_dim = None
        self.forcefield = forcefield

    def init_modeller(self, topology, coordinates, unit=nanometer, fix=True):
        modeller = Modeller(topology, coordinates*unit)
        if fix:
            modeller.addExtraParticles(self.forcefield)
            modeller.addHydrogens(self.forcefield)
        self.modeller = modeller

    def modeller_from_MDtraj(self, traj):
        top = traj.topology.to_openmm()
        pos = np.array(traj.openmm_positions(0).value_in_unit(nanometer))
        self.init_modeller(top, pos)
        return top, pos

    def solvate_modeller(self, **kwargs):
        self.modeller.addSolvent(self.forcefield, **kwargs)

    def desolvate_modeller(self):
        self.modeller.deleteWater()

    def set_box_dim(self, nstd=3):
        dmat = distance_matrix(self.modeller.positions.value_in_unit(nanometers),
                               self.modeller.positions.value_in_unit(nanometers))
        self.box_dim = nstd*max(1, dmat.std()) + dmat.max()
        return self.box_dim

class EnsembleSimulator:
    def __init__(self, ff_solute, ff_solvent):
        self.forcefield = ForceField(ff_solute, ff_solvent)
        self.simulation = None
        self.modeller = None
        self.box_dim = None
        self.MW = ModellerWrapper(self.forcefield)

    def add_ensemble_forces(self, system):
        raise Exception ("Ensemble required! Use a subclass instead: NPTSimulator or NVTSimulator")

    def init_system(self):
        system = self.forcefield.createSystem(self.top,
                                              nonbondedMethod=PME,
                                              nonbondedCutoff=1*nanometer,
                                              constraints=HBonds,
                                              hydrogenMass=1.5*amu)
        return system

    def simulation_from_system(self, system, temperature, dt):
        timestep, timeunit = decomposeQuantity(dt)
        integrator = LangevinMiddleIntegrator(temperature, 1/timeunit, dt)
        self.simulation = Simulation(self.top, system, integrator,
                                     platform=openmm.Platform.getPlatformByName('CUDA'))
        self.simulation.context.setPositions(self.pos)
        self.simulation.context.setVelocitiesToTemperature(temperature)
        return self.simulation

    def init_simulation(self, **ensemble_args):
        system = self.init_system()
        system = self.add_ensemble_forces(system, **ensemble_args)
        self.simulation = self.simulation_from_system(system, ensemble_args['temperature'], ensemble_args['dt'])

    def modeller_from_MDtraj(self, traj):
        self.top, self.pos = self.MW.modeller_from_MDtraj(traj)

    def extract_top_pos(self, obj):

        if isinstance(obj, mdtraj.Trajectory):
            self.top = traj.topology.to_openmm()
            self.pos = np.array(traj.openmm_positions(0).value_in_unit(nanometer))

        elif isinstance(obj, openmm.app.PDBFile):
            self.top = obj.topology
            self.pos = obj.getPositions().value_in_unit(nanometer)

        elif isinstance(obj, openmm.app.Modeller):
            self.top = obj.topology
            self.pos = obj.getPositions()

        return self.top, self.pos


    def prepare_minimization(self, **ensemble_args):
        self.MW.set_box_dim()
        self.MW.solvate_modeller(neutralize=False,
                              boxSize=Vec3(self.MW.box_dim, self.MW.box_dim, self.MW.box_dim)*nanometers,
                              ionicStrength=0*molar,
                              model='tip4pew')
        self.MW.desolvate_modeller()
        self.top, self.pos = self.extract_top_pos(self.MW.modeller)
        self.init_simulation(**ensemble_args)

    def prepare_equilibration(self, **ensemble_args):
        self.MW.solvate_modeller(neutralize=True,
                              ionicStrength=1*molar,
                              positiveIon='K+',
                              negativeIon='Cl-',
                              model='tip4pew')
        self.top, self.pos = self.extract_top_pos(self.MW.modeller)
        self.init_simulation(**ensemble_args)

    def clear_ensemble_forces(self, simulation):
        thermostats = [idx for idx, force in enumerate(simulation.system.getForces())
                       if 'Thermostat' in force.getName()]
        barostats = [idx for idx, force in enumerate(simulation.system.getForces())
                     if 'Barostat' in force.getName()]
        if barostats:
            simulation.system.removeForce(*barostats)
        if thermostats:
            simulation.system.removeForce(*thermostats)
        return simulation

    def transfer_modeller(self, simulator):
        self.pos = simulator.simulation.context.getState(getPositions=True).getPositions()
        self.top = simulator.simulation.topology
        self.MW.init_modeller(self.top, self.pos.value_in_unit(nanometer), fix=False)

    def transfer_simulation(self, simulator, **ensemble_args):
        self.simulation = self.clear_ensemble_forces(simulator.simulation)
        self.add_ensemble_forces(self.simulation.system, **ensemble_args)

    def init_reporters(self, *args):
        for reporter in args:
            self.simulation.reporters.append(reporter)

    def simulate(self, num_steps):
        self.simulation.step(num_steps)

    def minimize(self, **kwargs):
        self.simulation.minimizeEnergy(**kwargs)

    def write_state_to_pdb(self, path):
        positions = self.simulation.context.getState(getPositions=True).getPositions()
        PDBFile.writeFile(self.simulation.topology, positions, open(path, 'w'))

    def simulation_from_checkpoint(self, path):
        self.simulation.loadCheckpoint(path)

    def simulation_from_state(self, path):
        self.simulation.loadState(path)

    def save_state(self, path):
        self.simulation.saveState(path)

    def save_checkpoint(self, path):
        self.simulation.saveCheckpoint(path)

class NPTSimulator(EnsembleSimulator):
    def __init__(self, ff_solute, ff_solvent):
        super().__init__(ff_solute, ff_solvent)

    def add_ensemble_forces(self, system, **kwargs):
        timestep, timeunit = decomposeQuantity(kwargs['dt'])
        system.addForce(MonteCarloBarostat(kwargs['pressure'], kwargs['temperature']))
        system.addForce(AndersenThermostat(kwargs['temperature'], 1/timeunit))
        return system

class NVTSimulator(EnsembleSimulator):
    def __init__(self, ff_solute, ff_solvent):
        super().__init__(ff_solute, ff_solvent)

    def add_ensemble_forces(self, system, **kwargs):
        timestep, timeunit = decomposeQuantity(kwargs['dt'])
        system.addForce(AndersenThermostat(kwargs['temperature'], 1/timeunit))
        return system



