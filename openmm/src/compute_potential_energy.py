#!/usr/bin/env python

import MDAnalysis as mda
import numpy as np
import parmed as pmd
from openmm.app import Modeller, ForceField, Simulation, PDBFile, PDBxFile
from openmm.unit import *
from openmm import LangevinMiddleIntegrator
import openmm
import os
import time
import datetime
import argparse


def select_near_nucleic(u, rad=5):
    nucleic = 'resname [GACU]'
    nucleic_sel = u.select_atoms(nucleic)
    near_nucleic = f"around {rad} resname [GACU]"
    near_nucleic_sel = u.select_atoms(near_nucleic)
    if near_nucleic_sel.n_atoms != 0:
        whole_res_near_nucleic = f'resid {" ".join(np.array(list(set(near_nucleic_sel.atoms.resids))).astype(str))}'
        whole_res_near_nucleic_sel = u.select_atoms(whole_res_near_nucleic)
        all_near = near_nucleic_sel.union(whole_res_near_nucleic_sel).union(nucleic_sel)
    else:
        all_near = nucleic_sel

    return all_near


parser = argparse.ArgumentParser()
parser.add_argument('--pdbid', required=True,
                    type=str, help="master yaml file is required")
parser.add_argument('--structid', required=True,
                    type=str, help="simulation specific yaml file is required")
parser.add_argument('--rad', required=True,
                    type=str, help="simulation specific yaml file is required")
parser.add_argument('--base_path', required=True,
                    type=str, help="simulation specific yaml file is required")
args = parser.parse_args()

pdbid = args.pdbid
i = args.structid
rad = args.rad
base_path = args.base_path

top = os.path.join(base_path, f"{pdbid}_struct{i}_sol.pdb")
pdb_top_path = os.path.join(base_path, f"{pdbid}_struct{i}_sol.pdb")
pdbx_top_path = os.path.join(base_path, f"{pdbid}_struct{i}_sol.cif")
traj_path = os.path.join(base_path, f"{pdbid}_struct{i}.xtc")

pdb_top = PDBFile(pdb_top_path)
PDBxFile.writeFile(pdb_top.topology, pdb_top.positions, open(pdbx_top_path, 'w'))
pdbx_top = PDBxFile(pdbx_top_path)

u = mda.Universe(pdb_top, traj_path)

energies = []
start_time = int(time.time())
print_freq = 10
save_freq = 1000
for frame_num, ts in enumerate(u.trajectory, 1):
    all_near = select_near_nucleic(u, rad=rad)
    forcefield = ForceField('amber14/RNA.Shaw_charmm22-ions.xml', 'amber14/tip4pd_desres.xml')
    struct_pdb = all_near.convert_to('PARMED')
    struct_pdbx = pmd.openmm.load_topology(pdbx_top.topology)[all_near.atoms.indices]
    modeller = Modeller(struct_pdbx.topology, struct_pdb.coordinates/10)
    modeller.addExtraParticles(forcefield)
    subsystem = forcefield.createSystem(modeller.topology)
    integrator = LangevinMiddleIntegrator(310*kelvin, 1/picosecond, 0.0005*picoseconds)
    simulation = Simulation(modeller.topology, subsystem, integrator)
    simulation.context.setPositions(modeller.positions)
    state = simulation.context.getState(getEnergy=True, groups={0})
    energies.append(state.getPotentialEnergy() / openmm.unit.kilocalorie_per_mole)
    if frame_num % print_freq == 0:
        elapsed_time = time.time() - start_time
        time_remaining = (u.trajectory.n_frames - frame_num) * (elapsed_time/frame_num)
        start_time = elapsed_time
        print(f"{pdbid}, struct:{i}, frame:{frame_num}, time_to_completion: {str(datetime.timedelta(0, time_remaining)).split('.')[0]} (HH:MM:SS)")
    if frame_num % save_freq == 0:
        np.save(os.path.join(base_path, f"{pdbid}_struct{i}_energies.npy"), np.array(energies))

np.array(energies)
np.save(os.path.join(base_path, f"{pdbid}_struct{i}_energies.npy"), energies)
