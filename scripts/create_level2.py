"""
Script to convert level 1 data
to level 2 data

This level2 dataset includes:
   - masks for each classification

The output is an array with the dimensions
    classification_ids x image_x x image_y x 4
"""

# Path to zooniverse files
clas_fn = '../zooniverse_raw/sugar-flower-fish-or-gravel-classifications.csv'
subj_fn = '../zooniverse_raw/sugar-flower-fish-or-gravel-subjects.csv'

# Level1 filename
level1_file = '../processed_data/EUREC4A_ManualClassifications_l1.nc'

# Level2 filename
level2_file = '../processed_data/EUREC4A_ManualClassifications_MergedClassifications.zarr'

# Define subject sets of interest
subjs_of_interest = [81160, 81382, 80697, 80696]

import sys
# Path to pycloud folder (https://github.com/raspstephan/sugar-flower-fish-or-gravel/tree/master/pyclouds)
sys.path.append("/Users/haukeschulz/Documents/PhD/Work/Own/AI_CloudClassification/CloudClassificationDay/cloud-classification/")

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
from helpers import *

logging.info('Open Level1 file')
ds_l1 = xr.open_dataset(level1_file)
df_l1 = ds_l1.to_dataframe()

boxes_arr = np.empty(len(df_l1.groupby('classification_id')),dtype=object)
for c, (clas_id, clas_df) in enumerate(df_l1.groupby('classification_id')):
    boxes = clas_df.loc[:,['x','y','width','height','tool_label']].values
    boxes_arr[c] = boxes

# Create file and calculate common boxes
logging.info('Level2 data creation started')
z_arr = zarr.convenience.open(level2_file, mode='a',
              shape=(len(np.unique(df_l1.classification_id)), 2200, 1500, 4),
              chunks=(1, 2200, 1500, 4), dtype=bool)

for b, box in enumerate(tqdm.tqdm(boxes_arr)):
    z_arr[b,:,:,:] = most_common_boxes(box,return_all_pattern=True,imag_dim=(2200,1500))

logging.info('Level2 data creation completed')
