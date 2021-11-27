"""
Script to convert level 1 data
to level 2 data

This level2 dataset includes:
   - masks for each classification

The output is an array with the dimensions
    classification_ids x image_x x image_y x 4
"""

import sys
from omegaconf import OmegaConf as oc
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
conf = oc.load(args['configfile'])
# Path to pycloud folder (https://github.com/raspstephan/sugar-flower-fish-or-gravel/tree/master/pyclouds)
sys.path.append(conf.env.pyclouds)

sys.path.append("../helpers/")

import os
import subprocess
import time
import tqdm
import numpy as np
import pandas as pd
import datetime as dt
import logging
import dask.array as da
import xarray as xr
import zarr
from numcodecs import Blosc
from pyclouds import *
import general_helpers as g
from helpers import *

g.setup_logging(args['verbose'])

classification = args['classification']


# Level1 filename
level1_file = conf[classification].level1.fn_netcdf

# Level2 filename
level2_file = conf[classification].level2.fn_zarr


try:
    git_module_version = subprocess.check_output(["git", "describe", "--dirty"]).strip().decode("utf-8")
except:
    git_module_version = "--"

logging.info('Open Level1 file')
ds_l1 = xr.open_dataset(level1_file)
df_l1 = ds_l1.to_dataframe()

nb_classifications = len(np.unique(df_l1.classification_id))
nb_lats = 1500
nb_lons = 2200
nb_patterns = 4

boxes_arr = np.empty(len(df_l1.groupby('classification_id')),dtype=object)
for c, (clas_id, clas_df) in enumerate(df_l1.groupby('classification_id')):
    boxes = clas_df.loc[:,['x','y','width','height','tool_label']].values
    boxes_arr[c] = boxes

# Create file and calculate common boxes
logging.info('Level2 data creation started')
store = zarr.DirectoryStore(level2_file)
root_grp = zarr.group(store, overwrite=True)
mask = root_grp.create_dataset('mask', shape=(nb_classifications, nb_lons, nb_lats),
                               chunks=(10, 1100, 750),
                               dtype="i4", compressor=Blosc(blocksize=0,clevel=9,cname="zstd",shuffle=Blosc.BITSHUFFLE))
clas_ids = root_grp.create_dataset('classification_id', shape=(nb_classifications), chunks=(nb_classifications),
                        dtype="i4")
lats = root_grp.create_dataset('latitude', shape=(nb_lats), chunks=(nb_lats),
                        dtype="f4")
lons = root_grp.create_dataset('longitude', shape=(nb_lons), chunks=(nb_lons),
                        dtype="f4")


for b, box in enumerate(tqdm.tqdm(boxes_arr)):
    mask_ = most_common_boxes(box,return_all_pattern=True,imag_dim=(nb_lons,nb_lats)).astype(int)*np.array([1,2,4,8])
    mask[b,:,:] = np.sum(mask_,axis=-1)

clas_ids[:] = np.unique(df_l1.classification_id)
lons[:] = np.linspace(-62,-40,nb_lons)
lats[:] = np.linspace(20,5,nb_lats)

# Add attributes to file
# Variable attributes
mask.attrs['_ARRAY_DIMENSIONS'] = ('classification_id', 'longitude', 'latitude')
mask.attrs['description'] = 'classification mask for every single pattern and classification_id'
mask.attrs['flag_masks'] = [1,2,4,8]
mask.attrs['flag_meanings'] = ['Sugar', 'Flowers', 'Fish', 'Gravel']
lons.attrs['_ARRAY_DIMENSIONS'] = ('longitude')
lons.attrs['standard_name'] = 'longitude'
lons.attrs['units'] = 'degree_east'
lats.attrs['_ARRAY_DIMENSIONS'] = ('latitude')
lats.attrs['standard_name'] = 'latitude'
lats.attrs['units'] = 'degree_north'
clas_ids.attrs['_ARRAY_DIMENSIONS'] = ('classification_id')
clas_ids.attrs['description'] = 'classification id (basically each sighting of an image has a unique id)'

# Global attributes
root_grp.attrs['title'] = 'EUREC4A: manual meso-scale cloud pattern classifications'
root_grp.attrs['description'] = 'Level-2: classification masks'
root_grp.attrs['author'] = 'Hauke Schulz (hauke.schulz@mpimet.mpg.de)'
root_grp.attrs['institute'] = 'Max Planck Institut für Meteorologie, Germany'
root_grp.attrs['created_on'] = dt.datetime.now().strftime('%Y-%m-%d %H:%M UTC')
root_grp.attrs['created_with'] = os.path.basename(__file__) + " with its last modification on " + time.ctime(
            os.path.getmtime(os.path.realpath(__file__)))
root_grp.attrs['version'] = git_module_version
root_grp.attrs['python_version'] = "{}".format(sys.version)

zarr.consolidate_metadata(store)
logging.info('Level2 data creation completed')
