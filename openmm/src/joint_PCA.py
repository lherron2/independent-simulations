from utils import load_dict_from_npy, array_from_dict
import os
import numpy as np
from sklearn.decomposition import MiniBatchSparsePCA
import argparse

parser = argparse.ArgumentParser()
parser.add_argument('--pdbid',
                    required=True,
                    type=str)
parser.add_argument('--data_path',
                    required=False,
                    type=str)
args = parser.parse_args()

diffusion_file = os.path.join(args.data_path, f"{args.pdbid}_DDPM_gvecs.npy")
diffusion_dict = load_dict_from_npy(diffusion_file)

gvec_file = os.path.join(args.data_path, f"{args.pdbid}_MD_gvecs_flattened.npy")
gvec_dict = load_dict_from_npy(gvec_file)

diffusion_gvec_arr = array_from_dict(diffusion_dict)
MD_gvec_arr = array_from_dict(gvec_dict)

pca = MiniBatchSparsePCA(n_components=2, batch_size=100, alpha=0.)
pca_MD = pca.fit_transform(MD_gvec_arr[::10])

pca_MD_dict = {key: pca.transform(value) for
               key, value in gvec_dict.items()}
pca_DDPM_dict = {key: pca.transform(value) for
                 key, value in diffusion_dict.items()}

pca_DDPM_file = f"{args.pdbid}_DDPM_pca.npy"
pca_DDPM_path = os.path.join(args.data_path, pca_DDPM_file)
np.save(pca_DDPM_path, pca_DDPM_dict)

pca_MD_file = f"{args.pdbid}_MD_pca.npy"
pca_MD_path = os.path.join(args.data_path, pca_MD_file)
np.save(pca_MD_path, pca_MD_dict)
