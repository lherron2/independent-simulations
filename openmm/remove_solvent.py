import mdtraj as md
import argparse


parser = argparse.ArgumentParser()
parser.add_argument('--pdbid', required=True, 
                    type=str, help="master yaml file is required")
parser.add_argument('--structid', required=True, 
                    type=str, help="simulation specific yaml file is required")
args = parser.parse_args()
traj_filename = f'structure{args.structid}/{args.pdbid}_struct{args.structid}.xtc'
top_filename = f'structure{args.structid}/{args.pdbid}_struct{args.structid}_sol.pdb'

try:
    for i, chunk in enumerate(md.iterload(traj_filename, top=top_filename, chunk=1000)):
        if i == 0:
            no_sol = chunk.remove_solvent() 
        else:
            no_sol = no_sol.join(chunk.remove_solvent())
except: None
no_sol = no_sol.center_coordinates()    
no_sol = no_sol.superpose(no_sol).smooth(3)
no_sol.save_xtc(f'structure{args.structid}/{args.pdbid}_struct{args.structid}_nosol.xtc')
print("saved")
