import argparse
from traj_tools import TrajFixer

parser = argparse.ArgumentParser()
parser.add_argument('--broken_traj', required=True,
                    type=str, help="Path to broken trajectory file")
parser.add_argument('--broken_top', required=True,
                    type=str, help="Path to broken topology file")
parser.add_argument('--fixed_traj', required=True,
                    type=str, help="Path to fixed trajectory file")
parser.add_argument('--fixed_top', required=True,
                    type=str, help="Path to fixed topology")
args = parser.parse_args()    

TF = TrajFixer(args.broken_traj, args.broken_top)
fixed_traj, fixed_top = TF.fix_traj()
fixed_traj.save(args.fixed_traj)
fixed_top.save(args.fixed_top)