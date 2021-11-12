"""
Script to convert level 2 data
to level 3 data

This level3 dataset includes:
   - daily agreement mask for each workflow

The output is an array with the dimensions
    dates x image_x x image_y x 4
"""

# Define workflow and instrument combinations
combos = {'IR': {'workflow':'EUREC4A (IR)', 'instrument':['ABI']},
          'VIS': {'workflow':'EUREC4A (VIS)', 'instrument': ['ABI', 'MODIS']},
          'albedo': {'workflow':'EUREC4A (ICON; albedo)', 'instrument': ['', 'n/a']},
          'cliq': {'workflow':'EUREC4A (ICON; cloud liquid + ice)', 'instrument': ['', 'n/a']}
         }

import sys

# Load config
from omegaconf import OmegaConf as oc
conf = oc.load('config.yaml')
# Path to pycloud folder (https://github.com/raspstephan/sugar-flower-fish-or-gravel/tree/master/pyclouds)
sys.path.append(conf.env.pyclouds)

sys.path.append("../helpers/")

import os
import time
import tqdm
import numpy as np
import pandas as pd
import datetime as dt
import logging
import dask.array as da
import xarray as xr
import zarr
from pyclouds import *
import general_helpers as g
from helpers import *

g.setup_logging('INFO')

classification = 'EUREC4A'

# Level1 filename
level1_file = conf[classification].level1.fn_netcdf

# Level2 filename
level2_file = conf[classification].level2.fn_zarr

# Level3 filename
level3_file = conf[classification].level3.fn_zarr

# workflow = 'EUREC4A (VIS)'  # possible choices: 'EUREC4A (ICON; albedo)', 'EUREC4A (ICON; cloud liquid + ice)', 'EUREC4A (IR)', 'EUREC4A (VIS)']
# workflow_dict = {'EUREC4A (IR)': 'IR',
#                  'EUREC4A (ICON; albedo)': 'albedo',
#                  'EUREC4A (ICON; cloud liquid + ice)': 'cliq',
#                  'EUREC4A (VIS)': 'VIS'
#                 }

# # Define instrument of interest
# instrument = ['ABI']  # possible choices: '', 'ABI', 'MODIS', 'n/a'
# # instrument_dict = {'ABI': 'ABI',
# #                    'MODIS': 'MODIS',
# #                    '': '',
# #                    'n/a': ''
# #                   }


try:
    git_module_version = subprocess.check_output(["git", "describe", "--dirty"]).strip().decode("utf-8")
except:
    git_module_version = "--"

# Load level 1 data
ds_l1 = xr.open_dataset(level1_file)
df_l1 = ds_l1.to_dataframe()

# Load level 2 data
if os.path.exists(level2_file):
    # Open file for reading
    ds_l2 = xr.open_zarr(level2_file)
elif os.path.exists(level2_file+'.zip'):
    logging.error('Please unzip {} first an rerun.'.format(level2_file+'.zip'))
    sys.exit()
else:
    logging.error('Run create_level2.py to create the level2 data')

da_arr = ds_l2.mask

nb_lats = len(da_arr.latitude)
nb_lons = len(da_arr.longitude)
nb_patterns = len(da_arr.pattern)
nb_dates = len(df_l1.groupby(df_l1['date'].dt.date))

for combo, combo_details in combos.items():
    workflow = combo_details['workflow']
    instrument = combo_details['instrument']
    logging.info('Workflow: {}, instrument: {}'.format(workflow, instrument))

    logging.info('Level3 data creation started')
    store = zarr.DirectoryStore(level3_file.format(workflow=combo))
    root_grp = zarr.group(store, overwrite=True)
    freq = root_grp.create_dataset('freq', shape=(nb_dates, nb_lons, nb_lats, nb_patterns),
                                   chunks=(1, nb_lons, nb_lats, nb_patterns),
                                   dtype=float, compressor=zarr.Zlib(level=1))
    dates = root_grp.create_dataset('date', shape=(nb_dates), chunks=(nb_dates),
                            dtype=int, compressor=zarr.Zlib(level=1))
    nb_user = root_grp.create_dataset('nb_users', shape=(nb_dates), chunks=(nb_dates),
                            dtype=int, compressor=zarr.Zlib(level=1))
    lats = root_grp.create_dataset('latitude', shape=(nb_lats), chunks=(nb_lats),
                            dtype=float, compressor=zarr.Zlib(level=1))
    lons = root_grp.create_dataset('longitude', shape=(nb_lons), chunks=(nb_lons),
                            dtype=float, compressor=zarr.Zlib(level=1))
    patterns = root_grp.create_dataset('pattern', shape=(nb_patterns), chunks=(nb_patterns),
                            dtype=str, compressor=zarr.Zlib(level=1))

    for d, (date, date_df) in enumerate(tqdm.tqdm(df_l1.groupby(df_l1['date'].dt.date))):
        date_arr = np.zeros((len(np.unique(date_df.user_name)),
                             nb_lons,
                             nb_lats,
                             nb_patterns
                            ), dtype=bool)
        instrument_mask = np.in1d(date_df.instrument, instrument)
        date_df_sel = date_df.loc[np.logical_and(~date_df.already_seen.astype(bool),
                                                 np.logical_and(date_df.workflow_name == workflow ,
                                                                instrument_mask))]
        for u, (user_name, user_df) in enumerate(date_df_sel.groupby('user_name')):
            class_ids = user_df.classification_id
            class_ids = np.unique(class_ids)
            user_arr = da_arr.sel({'classification_id':class_ids}).sum(axis=0).compute()
            user_arr = np.where(user_arr>0, True, False)
            date_arr[u, :,:,:] = user_arr
        nb_user[d] = len(np.unique(date_df_sel.user_name))
        freq[d,:,:,:] = np.sum(date_arr[:,:,:,:], axis=0)/nb_user[d]

    for d, (date, date_df) in enumerate(df_l1.groupby(df_l1['date'].dt.date)):
        dates[d] = (date-dt.datetime(1970,1,1).date()).total_seconds()
    lons[:] = da_arr.longitude.values  # np.linspace(-62,-40,nb_lons)
    lats[:] = da_arr.latitude.values  # np.linspace(20,5,nb_lats)
    patterns[:] = ['Sugar', 'Flowers', 'Fish', 'Gravel']

    # Add attributes to file
    # Variable attributes
    freq.attrs['_ARRAY_DIMENSIONS'] = ('date', 'longitude', 'latitude', 'pattern')
    freq.attrs['description'] = 'classification frequency for every day'
    lons.attrs['_ARRAY_DIMENSIONS'] = ('longitude')
    lons.attrs['standard_name'] = 'longitude'
    lons.attrs['units'] = 'degree_east'
    lats.attrs['_ARRAY_DIMENSIONS'] = ('latitude')
    lats.attrs['standard_name'] = 'latitude'
    lats.attrs['units'] = 'degree_north'
    dates.attrs['_ARRAY_DIMENSIONS'] = ('date')
    dates.attrs['units'] = 'seconds since 1970-01-01 00:00:00 UTC'
    dates.attrs['standard_name'] = 'time'
    dates.attrs['calendar'] = 'standard'
    patterns.attrs['_ARRAY_DIMENSIONS'] = ('pattern')
    nb_user.attrs['_ARRAY_DIMENSIONS'] = ('date')
    nb_user.attrs['description'] = 'number of users that saw this image/dataset'

    # Global attributes
    root_grp.attrs['title'] = 'EUREC4A: manual meso-scale cloud pattern classifications'
    root_grp.attrs['description'] = 'Level-3: daily classification frequency'
    root_grp.attrs['author'] = 'Hauke Schulz (hauke.schulz@mpimet.mpg.de)'
    root_grp.attrs['institute'] = 'Max Planck Institut für Meteorologie, Germany'
    root_grp.attrs['created_on'] = dt.datetime.now().strftime('%Y-%m-%d %H:%M UTC')
    root_grp.attrs['created_with'] = os.path.basename(__file__) + " with its last modification on " + time.ctime(
                os.path.getmtime(os.path.realpath(__file__)))
    root_grp.attrs['version'] = git_module_version
    root_grp.attrs['python_version'] = "{}".format(sys.version)

    logging.info('Level3 data creation completed')
