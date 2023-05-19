#!/usr/bin/env python

import numpy as np
import os
import argparse
from simulation import load_config, replace_wildcards, add_args
from utils import get_simulation_dirs, convert_key_type, sort_dict_by_keys, save_dict_as_npy

parser = argparse.ArgumentParser()
parser.add_argument('--pdbid', required=True,
                    type=str)
parser.add_argument('--root_path',
                    required=True,
                    type=str)
parser.add_argument('--master_config',
                    required=True,
                    type=str)
parser.add_argument('--file_identifier',
                    required=True,
                    type=str)
parser.add_argument('--out_path',
                    required=True,
                    type=str)
parser.add_argument('--outfile',
                    required=True,
                    type=str)
parser.add_argument('--ext',
                    required=False,
                    default="npy",
                    type=str)
args = parser.parse_args()


master_config = load_config(args.master_config)

dirlist = get_simulation_dirs(args.root_path, master_config.identifier)
dict = {}
for dir in dirlist:
    master_config = load_config(args.master_config)
    sim_config = load_config(os.path.join(dir.path, "sim_prod.yaml"))
    master_config = replace_wildcards(master_config, sim_config)
    master_config = add_args(master_config, simtype=None)

    name_prefix=f"{master_config.pdbid}_{master_config.identifier}{sim_config.structid}"

    file = os.path.join(dir.path, f"{name_prefix}_{args.file_identifier}.npy")
    try:
        dict[sim_config.temperature] = np.load(file)
    except:
        dict[sim_config.temperature] = np.load(file, allow_pickle=True).item(0)

outfile = os.path.join(args.out_path, f"{args.outfile}.npy")
save_dict_as_npy(outfile, dict)
