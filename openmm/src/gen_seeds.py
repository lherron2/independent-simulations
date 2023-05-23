import numpy as np
import os
import mdtraj as md
import argparse
from deeptime.clustering import RegularSpace
from scipy.spatial import distance_matrix

def closest_node(centers, nodes):
    dist = distance_matrix(centers, nodes)
    dist = np.ma.masked_equal(dist, 0)
    return np.argmin(dist, axis=1), dist

parser = argparse.ArgumentParser()
parser.add_argument('--pdbid', required=True,
                    type=str, help="PDB ID used for naming simulation directories")
parser.add_argument('--traj', required=True,
                    type=str, help="Path to broken trajectory file")
parser.add_argument('--top', required=True,
                    type=str, help="Path to broken topology file")
parser.add_argument('--energy_file', required=True,
                    type=str, help="Path to energy .npy file")
parser.add_argument('--annot_file', required=True,
                    type=str, help="Path to annotation (base pair) .npy file")
parser.add_argument('--output_dir', required=True,
                    type=str, help="Path to initialize directory structure at. If output_dir does not exist it will be created.")
parser.add_argument('--num_structs', required=True,
                    type=int, help="Number of seeds to generate")
parser.add_argument('--d_min', required=False, default=None,
                    type=float, help="Minimum inter-centroid distance for regular space clustering")
args = parser.parse_args()

energy = np.load(args.energy_file)
BP = np.load(args.annot_file)

# restricting to stable structures
# i.e. structures with
# energy less than mean - std and
# base pairs more than mean - std

energy_cutoff = energy.mean()
BP_cutoff = BP.mean()
idxs = np.arange(len(BP))

stable_idxs = idxs[(energy<energy_cutoff)&(BP>BP_cutoff)]
stable_BPs = BP[(energy<energy_cutoff)&(BP>BP_cutoff)] + np.random.normal(0,0.25,len(stable_idxs))
stable_energy = energy[(energy<energy_cutoff)&(BP>BP_cutoff)]
stable_points = np.vstack([stable_BPs, stable_energy]).T
all_points = np.vstack([BP, energy]).T

# estimating the min inter-centroid distance
# for regular space clustering
counts, xe, ye = np.histogram2d(stable_BPs, stable_energy, bins=10)
dy, dx = ye[1] - ye[0], xe[1] - xe[0]
n_bins = len(counts[counts != 0])
area = n_bins*dy*dx
if args.d_min is None:
    d_min = (area/args.num_structs/np.pi)**0.5
else:
    d_min = args.d_min

# clustering over stable structures
estimator = RegularSpace(dmin=d_min, max_centers=10000, n_jobs=1)
model = estimator.fit(stable_points).fetch_model()
c_reps, dists = closest_node(model.cluster_centers, stable_points)

assert len(c_reps) > args.num_structs, "Not enough centroids! Try manually reducing --d_min."

# sorting seeds by base-pairedness
rsc_centroids = np.array(sorted(zip(stable_BPs[c_reps], stable_idxs[c_reps]), reverse=True)[:args.num_structs])
rsc_idxs = rsc_centroids[:,1].astype(int)
initial_seeds = all_points[rsc_idxs]

# initializing simulation directory structure
# with seed structures
seed_traj = md.load(args.traj, top=args.top)[rsc_idxs]
os.makedirs(args.output_dir, exist_ok=True)
seed_traj.save_xtc(os.path.join(args.output_dir, f"{args.pdbid}_seeds.xtc"))
seed_traj[0].save_pdb(os.path.join(args.output_dir, f"{args.pdbid}_seeds_top.pdb"))
for struct, frame in enumerate(seed_traj):
    struct_dir = os.path.join(args.output_dir, f"struct{struct}")
    os.makedirs(struct_dir, exist_ok=True)
    frame.save_pdb(os.path.join(struct_dir, f"{args.pdbid}_struct{struct}.pdb"))
