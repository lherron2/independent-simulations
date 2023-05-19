#!/usr/bin/env python

import argparse
import numpy as np
import os

parser = argparse.ArgumentParser()
parser.add_argument('--yaml',
                    type=str, help="path to yaml file required")
parser.add_argument('--sim_dir',
                    type=str, help="path to yaml file required")
parser.add_argument('--structid',
                    type=int, help="structid required")
parser.add_argument('--temperatures',
                    type=str, help="path to temperatures.npy required")
args = parser.parse_args()

temp = np.load(args.temperatures)[args.structid]
with open(args.yaml, 'r') as f:
        yaml = f.read()

yaml = yaml.replace("TEMP", str(temp)).replace("STRUCTID", str(args.structid))

yaml_fname = args.yaml.split('/')[-1]
with open(os.path.join(args.sim_dir, yaml_fname), 'w') as f:
    f.write(yaml)

