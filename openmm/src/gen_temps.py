import numpy as np
import os
import argparse

parser = argparse.ArgumentParser()
parser.add_argument('--min_temp', required=True, type=float)
parser.add_argument('--max_temp', required=True, type=float)
parser.add_argument('--num_structs', required=True, type=float)
parser.add_argument('--output_dir', required=True, type=str)
args = parser.parse_args()

spacing = int((args.max_temp - args.min_temp)/args.num_structs)
temps = np.arange(args.min_temp, args.max_temp, spacing)
np.save(os.path.join(args.output_dir, "temperatures.npy"), temps)
