"""
Script to anonymize the classifications

The user names can be deleted and only user ids
are kept.
"""
import argparse

def get_args():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('-c', '--configfile', help='Config file containing settings and paths for conversion', required=False, default='config.yaml')
    parser.add_argument('-e', '--classification', help="Choose which classification of those described in the configfile should be used",
                        required=True, default=None)
    parser.add_argument('-v', '--verbose', metavar="DEBUG",
                        help='Set the level of verbosity [DEBUG, INFO, WARNING, ERROR]',
                        required=False, default="INFO")

    args = vars(parser.parse_args())

    return args


args = get_args()

# Load config
from omegaconf import OmegaConf as oc
conf = oc.load(args['configfile'])

import numpy as np
import pandas as pd
import xarray as xr

classification = args['classification']

raw_data_filename_input = conf[classification].input.classifications_file
raw_data_filename_output = conf[classification].input.classifications_file_anonymous

level1_data_filename_input = conf[classification].level1.fn_netcdf
level1_data_filename_output = conf[classification].level1.fn_netcdf_anonymous

# Anonymize raw data

df = pd.read_csv(raw_data_filename_input)
if classification == "EUREC4A":
    df = df.iloc[38003:]  # remove data from other classification days
uniq_names = df['user_name'].unique()
uniq_ids = pd.Series(np.arange(len(uniq_names)))
anonymize_dict = {n:i for i,n in zip(uniq_ids, uniq_names)}
df['user_id'] = df['user_name'].apply(lambda x: anonymize_dict.get(x))
del df['user_name']
df.to_csv(raw_data_filename_output)

