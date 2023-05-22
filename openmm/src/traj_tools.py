#!/usr/bin/env python

import MDAnalysis as mda
import mdtraj as md
import pdbfixer
import parmed as pmd
import barnaba as bb

import openmm
from openmm import LangevinMiddleIntegrator
from openmm.app.internal.pdbstructure import PdbStructure
from openmm.app import Modeller, ForceField, Simulation, PDBFile, PDBxFile
from openmm.unit import *

from simulation import LightweightSimulator
from utils import *

import numpy as np
import io
import os
import time
import datetime
import argparse


def apply_fixer(fixer):
    fixer.findNonstandardResidues()
    fixer.replaceNonstandardResidues()
    fixer.findMissingResidues()
    fixer.findMissingAtoms()
    fixer.addMissingAtoms()
    fixer.addMissingHydrogens()
    return fixer

def make_virtual_PDBFile(top, positions):
    handle = io.StringIO()
    openmm.app.PDBFile.writeFile(top, positions, handle, keepIds=True)
    file = io.StringIO(handle.getvalue())
    return file

def fix_PDBFile(file):
    """
    Takes in openmm topology and trajectory information and fills in missing atoms.
    """
    fixer = pdbfixer.PDBFixer(pdbfile=file)
    fixer = apply_fixer(fixer)
    file_out = make_virtual_PDBFile(fixer.topology, fixer.positions)
    structure = PdbStructure(file_out)
    pdb = openmm.app.PDBFile(structure)
    return pdb

def fix_mdtraj(traj, unit=angstrom):
    vtraj = fix_PDBFile(make_virtual_PDBFile(traj.topology.to_openmm(),
                                             traj.openmm_positions(0)))
    return md.Trajectory(np.array(vtraj.positions.value_in_unit(unit)),
                         md.Topology.from_openmm(vtraj.topology))

def compute_gvec_from_traj(traj):
    gvecs,seq = bb.dump_gvec_traj(traj)
    (n_samp, _, _, _) = gvecs.shape
    gvecs_flattened = gvecs.reshape(n_samp,-1)
    return gvecs, gvecs_flattened

def compute_rvec_from_traj(traj):
    rvecs,seq = bb.dump_rvec_traj(traj)
    (n_samp, _, _, _) = rvecs.shape
    rvecs_flattened = rvecs.reshape(n_samp,-1)
    return rvecs, rvecs_flattened

def annotate_base_pairs(traj, regex='(?!XXX)'):
    """
    regex excludes misformed base pairs.
    """
    stackings, pairings, seq = bb.annotate_traj(traj)
    annot = np.array([len(regex_list(regex, annot)) for pair, annot in pairings])
    return annot

def load_traj_from_xtc(dir, traj, top, name_prefix):
    nosol_xtc = os.path.join(dir.path, f"{name_prefix}_nosol.xtc")
    topology = md.load(top_path).topology
    traj = md.load(nosol_xtc, top=topology).center_coordinates()
    return traj, float(param)

class ForceFieldEvaluator:

    def __init__(self, solute_forcefield, solvent_forcefield):

        self.simulator = LightweightSimulator(solute_forcefield, solvent_forcefield)

    def get_updating_selections(self, u, selection, rad):

        solute = u.select_atoms(f'{selection}', updating=True)
        near_solute = u.select_atoms(f"around {rad} {selection}", updating=True)
        return solute, near_solute

    def get_whole_residues(self, u, solute, near_solute):

        if near_solute.n_atoms != 0:
            sel_resids = f'resid {" ".join(np.array(list(set(near_solute.resids))).astype(str))}'
            sel_res = u.select_atoms(sel_resids)
            all_sel = near_solute.union(sel_res).union(solute)
        else:
            all_sel = solute
        return all_sel

    def extract_frame(self, sel, vtop):

        coords = sel.convert_to('PARMED').coordinates
        top = vtop.atom_slice(sel.atoms.indices).topology.to_openmm()
        return coords, top

    def eval_ff_on_frame(self, simulator, top, coords, unit=angstrom):

        simulation = simulator.spawn_simulation(top, coords, unit=unit)
        energy = simulator.get_potential_energy(simulation)
        return energy

    def eval_traj(self, topology, trajectory, selection, rad, print_freq=100):

        print(f"topology {topology}")
        print(f"trajectory {trajectory}")
        u = mda.Universe(topology, trajectory, refresh_offsets=True)
        vtop = fix_mdtraj(md.load(topology))
        solute, near_solute = self.get_updating_selections(u, selection, rad)
        energies = []
        start_time = int(time.time())
        for frame_num, ts in enumerate(u.trajectory, 1):
            sel = self.get_whole_residues(u, solute, near_solute)
            coords, top = self.extract_frame(sel, vtop)
            energy = self.eval_ff_on_frame(self.simulator, top, coords)
            energies.append(energy)
            if frame_num % print_freq == 0:
                elapsed_time = time.time() - start_time
                time_remaining = (u.trajectory.n_frames - frame_num) * (elapsed_time/frame_num)
                print(f"frame:{frame_num}, energy:{energy:.0f}, time_to_completion: {str(datetime.timedelta(0, time_remaining)).split('.')[0]} (HH:MM:SS)")
        return np.array(energies)

class TrajFixer:

    def __init__(self, broken_traj, broken_top):

        self.traj = md.load(broken_traj, top=broken_top)

    def fix_frame(self, omm_topology, omm_positions, unit=angstrom, rescale_factor=10):

        pdb = make_virtual_PDBFile(omm_topology, omm_positions)
        fixed_pdb = fix_PDBFile(pdb)
        positions = fixed_pdb.getPositions().value_in_unit(unit)
        fixed_frame = md.Trajectory(np.array(positions)/rescale_factor, md.Topology.from_openmm(fixed_pdb.topology))
        return fixed_frame, fixed_pdb

    def fix_traj(self):

        frames = []
        start_time = int(time.time())
        for frame in range(self.traj.n_frames):
            fixed_frame, fixed_pdb = self.fix_frame(self.traj.topology.to_openmm(),
                                                    self.traj.openmm_positions(frame))
            if frame == 0:
                fixed_top = fixed_frame
                fixed_traj = fixed_frame
            else:
                fixed_traj = fixed_traj.join(fixed_frame)

            if frame % 10 == 0:
                elapsed_time = time.time() - start_time
                time_remaining = (self.traj.n_frames - frame) * (elapsed_time/(frame+1))
                print(f"frame:{frame}, time_to_completion: {str(datetime.timedelta(0, time_remaining)).split('.')[0]} (HH:MM:SS)")
        return fixed_traj, fixed_top

