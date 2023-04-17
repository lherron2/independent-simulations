from utils import *
import os
import barnaba as bb
import numpy as np
import re
import mdtraj as md
import argparse

def load_diffusion_data(diffusion_path):
    dirlist = get_sample_dirs(diffusion_path)
    diffusion_dict = {}
    for dir in dirlist:
        temp = get_temperature_from_dirname(dir)
        data = np.concatenate([np.load(file.path)['traj'] for file in os.scandir(dir.path)
                               if ('npz' in file.name)])
        (n_samp, _, _, _) = data.shape
        diffusion_dict[temp] = data.reshape(n_samp, -1)
    diffusion_dict = sort_dict_by_keys(diffusion_dict)
    return diffusion_dict

if __name__ == "__main__":

    parser = argparse.ArgumentParser()
    parser.add_argument('--pdbid', required=True,
                        type=str)

    parser.add_argument('--diffusion_path',
                    required=False,
                    type=str)

    parser.add_argument('--data_path',
                    required=False,
                    type=str)

    args = parser.parse_args()

    # loading diffusion samples and saving in npy file
    diffusion_dict = load_diffusion_data(args.diffusion_path)
    diffusion_file = os.path.join(args.data_path, f"{args.pdbid}_DDPM_gvecs.npy")
    save_dict_as_npy(diffusion_file, diffusion_dict)
