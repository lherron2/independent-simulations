import argparse
import numpy as np

parser = argparse.ArgumentParser()
parser.add_argument('f',
                    type=str, help="yaml file required")
parser.add_argument('structid',
                    type=int, help="structid required")
parser.add_argument('temperatures',
                    type=str, help="temperatures.npy required")
args = parser.parse_args()

temp = np.load(args.temperatures)[args.structid]

with open(args.f, 'r') as f:
        yaml = f.read()

yaml = yaml.replace("TEMP", str(temp)).replace("STRUCTID", str(args.structid))

with open(f"structure{args.structid}/" + args.f, 'w') as f:
    f.write(yaml)

