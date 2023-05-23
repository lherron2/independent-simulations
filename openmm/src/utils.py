#!/usr/bin/env python

import numpy as np
import os
import re
import yaml

def get_simulation_dirs(base_path, identifier):
    dirlist = [d for d in os.scandir(base_path) if
               (d.is_dir() and identifier == re.sub(r'[0-9]', '', d.name))]
    return dirlist

def get_structid_from_dirname(dir, identifier):
    return dir.name.split(identifier)[-1]

def sort_dict_by_keys(dict):
    return {k:dict[k] for k in sorted(dict.keys())}

def convert_key_type(dict, type):
    return {type(k):dict[k] for k in dict.keys()}

def load_yaml(file):
    with open(file, 'r') as stream:
            yaml_loaded = yaml.safe_load(stream)
    return yaml_loaded

def save_dict_as_npz(filepath, dict):
    energy_dict = sort_dict_by_keys(dict)
    energy_dict = convert_key_type(dict, str)
    np.savez(filepath, **energy_dict)

def save_dict_as_npy(file, dict):
    dict = sort_dict_by_keys(dict)
    np.save(file, dict)

def load_dict_from_npy(file):
    dict = np.load(file, allow_pickle=True).item(0)
    return dict

def array_from_dict(dict):
    return np.concatenate([v for v in dict.values()])

def get_temperature_from_dirname(dir):
    return dir.name[:-1]

def get_sample_dirs(path):
    dirlist = [d for d in os.scandir(path) if
               (d.is_dir() and 'K' == re.sub(r'[0-9]', '', d.name))]
    return dirlist

def regex_list(regex, l):
    return list(filter(re.compile(regex).match, l))


