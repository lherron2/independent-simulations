#!/usr/bin/env python

import mdtraj as md
import numpy as np
import argparse
import subprocess
import yaml
import os

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
    simulation_indices = np.array([int(i.split(xtc_string)[-1].split('.xtc')[0]) for i in xtc_list])
    simulation_index = max(simulation_indices) + 1
    return simulation_index

parser = argparse.ArgumentParser()
parser.add_argument('--pdbid', required=True,
                    type=str, help="master yaml file is required")
parser.add_argument('--structid', required=True,
                    type=str, help="simulation specific yaml file is required")
parser.add_argument('--master_yaml', required=True,
                    type=str, help="simulation specific yaml file is required")

args = parser.parse_args()

master_prod_params = load_yaml(args.master_yaml)
identifier = master_prod_params["identifier"]
data_path = master_prod_params["data_path"]
data_path = data_path.replace("PDBID", args.pdbid).replace("STRUCTID", str(args.structid))


top = f'{args.pdbid}_{identifier}{args.structid}_sol.pdb'
top_filename = os.path.join(data_path, top)
num_sims = get_simulation_idx(data_path, args.pdbid, args.structid, identifier)

for sim_idx in range(num_sims):
    traj = f'{args.pdbid}_{identifier}{args.structid}_{sim_idx}.xtc'
    traj_filename = os.path.join(data_path, traj)
    try:
        for i, chunk in enumerate(md.iterload(traj_filename, top=top_filename, chunk=10)):
            if sim_idx == 0:
                no_sol = chunk.remove_solvent()
            else:
                no_sol = no_sol.join(chunk.remove_solvent())
    except: None

no_sol = no_sol.center_coordinates()
no_sol = no_sol.superpose(no_sol).smooth(3)
nosol_filename = os.path.join(data_path, f'{args.pdbid}_{identifier}{args.structid}_nosol.xtc')
no_sol.save_xtc(nosol_filename)
print("saved")
