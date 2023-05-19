import argparse
import numpy as np
from traj_tools import ForceFieldEvaluator

parser = argparse.ArgumentParser()
parser.add_argument('--rad', required=True,
                    type=str, help="Radius of solvation shell (in Angstroms) ")
parser.add_argument('--sel', required=True,
                    type=str, help="Resname of the solute")
parser.add_argument('--top', required=True,
                    type=str, help="Topology of the system being analyzed (as pdb in nm)")
parser.add_argument('--traj', required=True,
                    type=str, help="Trajectory being analyzed (supports any format used by mdanalysis)")
parser.add_argument('--solute_ff', required=True,
                    type=str, help="Forcefield for the solute")
parser.add_argument('--solvent_ff', required=True,
                    type=str, help="Forcefield for the solvent")
parser.add_argument('--outfile', required=True,
                    type=str, help="Output filename (saved in same directory as topology and trajectory")
args = parser.parse_args()

print(args.sel)

FFE = ForceFieldEvaluator(args.solute_ff, args.solvent_ff)
energies = FFE.eval_traj(args.top, args.traj, args.sel, args.rad)
np.save(args.outfile, energies)
