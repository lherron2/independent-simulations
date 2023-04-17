from utils import *
import os
import barnaba as bb
import numpy as np
import re
import mdtraj as md
import argparse

def regex_list(regex, l):
    return list(filter(re.compile(regex).match, l))

def load_traj_from_xtc(root_path, identifier, pdbid, topology, parameter='temperature'):
    dirlist = get_simulation_dirs(root_path, identifier)
    traj_dict = {}
    for dir in dirlist:
        structid = get_structid_from_dirname(dir, identifier)
        temp = load_yaml(os.path.join(dir.path, "sim_prod.yaml"))[parameter]
        nosol_xtc = os.path.join(dir.path, f"{pdbid}_{identifier}{structid}_nosol.xtc")
        traj_dict[temp] = md.load(nosol_xtc, top=topology).center_coordinates()
    traj_dict = sort_dict_by_keys(traj_dict)
    return traj_dict

def compute_gvec_from_traj(traj_dict):
    gvec_dict = {}
    for temp, traj in traj_dict.items():
        gvec,seq = bb.dump_gvec_traj(traj)
        (n_samp, _, _, _) = gvec.shape
        gvec_dict[temp] = gvec.reshape(n_samp,-1)
    return gvec_dict

def annotate_base_pairs(traj_dict, regex='(?!XXX)'):
    """
    regex excludes misformed base pairs.
    """
    annot_dict = {}
    for temp, traj in traj_dict.items():
        stackings, pairings, seq = bb.annotate_traj(traj)
        annot = np.array([len(regex_list(regex, annot)) for pair, annot in pairings])
        annot_dict[temp] = annot
        print(temp)
    return annot_dict

if __name__ == "__main__":

    parser = argparse.ArgumentParser()
    parser.add_argument('--pdbid', required=True,
                        type=str)

    parser.add_argument('--root_path',
                        required=False,
                        default=os.getcwd(),
                        type=str)

    parser.add_argument('--data_path',
                    required=False,
                    default=os.getcwd(),
                    type=str)

    parser.add_argument('--diffusion_path',
                    required=False,
                    default=os.getcwd(),
                    type=str)

    parser.add_argument('--topology_path',
                    required=False,
                    default=os.getcwd(),
                    type=str)

    parser.add_argument('--master_yaml',
                        required=False,
                        default=os.path.join(os.getcwd(), "master_prod.yaml"),
                        type=str)
    args = parser.parse_args()

    identifier = load_yaml(args.master_yaml)['identifier']

    # loading xtc files and saving in npy file
    traj_dict = load_traj_from_xtc(args.root_path, identifier, args.pdbid,
                       args.topology_path, parameter='temperature')
    traj_file = os.path.join(args.data_path, f"{args.pdbid}_MD_traj.npy")
    save_dict_as_npy(traj_file, traj_dict)

    # computing g-vectors and saving in npy file
    gvec_dict = compute_gvec_from_traj(traj_dict)
    gvec_file = os.path.join(args.data_path, f"{args.pdbid}_MD_gvecs.npy")
    save_dict_as_npy(gvec_file, gvec_dict)

    # computing base-pairs and saving in npy file
    annot_dict = annotate_base_pairs(traj_dict)
    annot_file = os.path.join(args.data_path, f"{args.pdbid}_MD_annot.npy")
    save_dict_as_npy(annot_file, annot_dict)
