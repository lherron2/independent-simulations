import numpy as np
import mdtraj as md
import argparse
from traj_tools import annotate_base_pairs


parser = argparse.ArgumentParser()
parser.add_argument('--traj',
                    required=True,
                    type=str)
parser.add_argument('--top',
                    required=True,
                    type=str)
parser.add_argument('--outfile',
                    required=True,
                    type=str)
args = parser.parse_args()

traj = md.load(args.traj, top=args.top)
annot = annotate_base_pairs(traj)
np.save(args.outfile, annot)
