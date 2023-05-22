import os
import numpy as np
import mdtraj as md
import argparse
from traj_tools import load_traj_from_xtc, compute_gvec_from_traj, compute_rvec_from_traj, annotate_base_pairs
from simulation import load_config, replace_wildcards, add_args
from utils import get_simulation_dirs, convert_key_type, sort_dict_by_keys

parser = argparse.ArgumentParser()
parser.add_argument('--root_path',
                    required=False,
                    default=os.getcwd(),
                    type=str)
parser.add_argument('--data_path',
                    required=False,
                    default=os.getcwd(),
                    type=str)
parser.add_argument('--topology',
                    required=False,
                    default=os.getcwd(),
                    type=str)
parser.add_argument('--master_config',
                    required=True,
                    type=str)
args = parser.parse_args()

master_config = load_config(args.master_config)

# loading xtc files
print("Loading xtc files ...")
traj_dict = {}
for dir in get_simulation_dirs(args.root_path, master_config.identifier):

    print(dir.path)
    master_config = load_config(args.master_config)
    sim_config = load_config(os.path.join(dir.path, "sim_prod.yaml"))
    master_config = replace_wildcards(master_config, sim_config)
    master_config = add_args(master_config, simtype=None)

    name_prefix=f"{master_config.pdbid}_{master_config.identifier}{sim_config.structid}"
    nosol_xtc = os.path.join(dir.path, f"{name_prefix}_nosol.xtc")
    traj_dict[sim_config.temperature] = md.load(nosol_xtc, top=args.topology).center_coordinates()


traj_dict = convert_key_type(traj_dict, int)
traj_dict = sort_dict_by_keys(traj_dict)
traj_file = os.path.join(args.data_path, f"{master_config.pdbid}_MD_traj.npy")
np.save(traj_file, traj_dict)

# computing g-vectors and saving in npy file
print("computing gvecs ...")
gvec_dict = {}
gvec_flattened_dict = {}
for k, traj in traj_dict.items():
    print(k)
    gvecs, gvecs_flattened = compute_gvec_from_traj(traj)
    gvec_dict[k] = gvecs
    gvec_flattened_dict[k] = gvecs_flattened
gvec_file = os.path.join(args.data_path, f"{master_config.pdbid}_MD_gvecs.npy")
gvec_flattened_file = os.path.join(args.data_path, f"{master_config.pdbid}_MD_gvecs_flattened.npy")
np.save(gvec_file, gvec_dict)
np.save(gvec_flattened_file, gvec_flattened_dict)

print("computing rvecs ...")
rvec_dict = {}
rvec_flattened_dict = {}
for k, traj in traj_dict.items():
    print(k)
    rvecs, rvecs_flattened = compute_rvec_from_traj(traj)
    rvec_dict[k] = rvecs
    rvec_flattened_dict[k] = rvecs_flattened
rvec_file = os.path.join(args.data_path, f"{master_config.pdbid}_MD_rvecs.npy")
rvec_flattened_file = os.path.join(args.data_path, f"{master_config.pdbid}_MD_rvecs_flattened.npy")
np.save(rvec_file, rvec_dict)
np.save(rvec_flattened_file, rvec_flattened_dict)

# computing base-pairs and saving in npy file
print("computing annots ...")
annot_dict = {}
for k, traj in traj_dict.items():
    print(k)
    annot = annotate_base_pairs(traj)
    annot_dict[k] = annot
annot_file = os.path.join(args.data_path, f"{master_config.pdbid}_MD_annot.npy")
np.save(annot_file, annot_dict)
