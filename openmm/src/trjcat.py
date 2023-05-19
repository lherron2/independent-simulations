#!/usr/bin/env python

import mdtraj as md
import numpy as np
import argparse
import subprocess
import yaml
import os

from simulation import load_config, replace_wildcards, add_args

def load_yaml(file):
    with open(file, 'r') as stream:
            yaml_loaded = yaml.safe_load(stream)
    return yaml_loaded

def bash(command):
    "submits a command to the terminal. Particularly useful for text manipulation commands"
    output = subprocess.check_output(command, shell=True).decode("utf-8").rstrip().split("\n")
    return output

def get_simulation_idx(data_path, name_prefix):
    xtc_string=f"{name_prefix}_"
    xtc_list = bash(f"ls {data_path} | grep '{xtc_string}[0-9]*\.xtc'")
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
parser.add_argument('--subsample',
                    required=True,
                    type=int)
parser.add_argument('--chunk_size',
                    required=True,
                    type=int)
parser.add_argument('--desolvate',
                    required=True,
                    type=str)
args = parser.parse_args()

master_config = load_config(args.master_config)
sim_config = load_config(args.sim_config)
master_config = replace_wildcards(master_config, sim_config)
master_config = add_args(master_config, simtype=None)
data_path = os.path.join('/'.join(master_config.seed_path.split('/')[:-1]))

name_prefix=f"{master_config.pdbid}_{master_config.identifier}{sim_config.structid}"
top = f'{name_prefix}_sol.pdb'
top_filename = os.path.join(data_path, top)
num_sims = get_simulation_idx(data_path, name_prefix)

for sim_idx in range(num_sims):
    traj = f'{name_prefix}_{sim_idx}.xtc'
    traj_filename = os.path.join(data_path, traj)
    try:
        for i, chunk in enumerate(md.iterload(traj_filename, top=top_filename, chunk=args.chunk_size)):
            print(f"chunk {i}")
            if sim_idx == 0 and i == 0:
                if eval(args.desolvate):
                    new_xtc = chunk.remove_solvent()
                else:
                    new_xtc = chunk
            else:
                if eval(args.desolvate):
                    ch = chunk.remove_solvent()
                else:
                    ch = chunk
                new_xtc = new_xtc.join(ch)
            print(new_xtc)
    except: None

new_xtc = new_xtc.center_coordinates()[::args.subsample]
new_xtc = new_xtc.superpose(new_xtc)
if eval(args.desolvate):
    xtc_outfile = os.path.join(data_path, f'{name_prefix}_nosol.xtc')
    npy_outfile = os.path.join(data_path, f'{name_prefix}_nosol.npy')
else:
    xtc_outfile = os.path.join(data_path, f'{name_prefix}_sol.xtc')
    npy_outfile = os.path.join(data_path, f'{name_prefix}_sol.npy')
new_xtc.save_xtc(xtc_outfile)
#np.save(npy_outfile, np.array(new_xtc))
