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

diffusion_file = os.path.join(args.data_path, f"{pdbid}_DDPM_gvecs.npy")
diffusion_dict = load_dict_from_npy(diffusion_file)

gvec_file = os.path.join(args.data_path, f"{pdbid}_MD_gvecs.npy")
gvec_dict = load_dict_from_npy(gvec_file)

diffusion_gvec_arr = array_from_dict(diffusion_dict)
MD_gvec_arr = array_from_dict(gvec_dict)

pca = MiniBatchSparsePCA(n_components=2, batch_size=10, alpha=0.2)
pca_MD = pca.fit_transform(MD_gvec_arr[::10])
pca_MD = pca.transform(MD_gvec_arr[::1])[:,:]
pca_DDPM = pca.transform(diffusion_gvec_arr[::1])[:,:]

pca_DDPM_file = f"{pdbid}_DDPM_pca.npy"
pca_DDPM_path = os.path.join(args.data_path, pca_DDPM_file)
np.save(pca_DDPM_path, pca_DDPM_file)

pca_MD_file = f"{pdbid}_MD_pca.npy"
pca_MD_path = os.path.join(args.data_path, pca_MD_file)
np.save(pca_MD_path, pca_MD_file)