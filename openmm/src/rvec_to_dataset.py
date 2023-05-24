import numpy as np
import argparse

parser = argparse.ArgumentParser()
parser.add_argument('--rvec_path', required=True,
                    type=str, help="Output filename for dataset")
parser.add_argument('--dataset_path', required=True,
                    type=str, help="Output filename for dataset")
args = parser.parse_args()


rvecs = np.load(args.rvec_path, allow_pickle=True).item(0)
data = []
for k, v in rvecs.items():
    v = v.astype(np.float32)
    (n_samp, n_bases, _, _) = v.shape
    v = v.reshape(n_samp, -1, n_bases, n_bases)
    temp_shape = list(v.shape)
    temp_shape[1] = 1
    temp_shape = tuple(temp_shape)
    temp_ch = np.ones(temp_shape)*k
    dequant = 2*np.random.uniform(size=temp_shape)-1
    temp_ch +=  dequant.astype(np.float32)
    data.append(np.concatenate([v, temp_ch], axis=1, dtype=np.float32))

data = np.concatenate(data, axis=0)
np.save(args.dataset_path, data)
