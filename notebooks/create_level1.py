"""
Script to convert zooniverse raw data
to level 1 data

This level1 dataset includes:
   - restructured rawdata
   - additional information about the subjects (e.g. instrument, capture time, init time)
   - overfloating classifications are reset to bounds
   - geographical coordinates are retrieved from pixel coordinates
"""

# Path to zooniverse files
clas_fn = '../zooniverse_raw/sugar-flower-fish-or-gravel-classifications.csv'
subj_fn = '../zooniverse_raw/sugar-flower-fish-or-gravel-subjects.csv'

# Level1 filename
level1_file = '../processed_data/EUREC4A_ManualClassifications_l1.nc'

# Define subject sets of interest
subjs_of_interest = [81160, 81382, 80697, 80696]

import sys
# Path to pycloud folder (https://github.com/raspstephan/sugar-flower-fish-or-gravel/tree/master/pyclouds)
sys.path.append("/Users/haukeschulz/Documents/PhD/Work/Own/AI_CloudClassification/CloudClassificationDay/cloud-classification/")

sys.path.append("../helpers/")

import os
import subprocess
import time
import tqdm
import logging
import numpy as np
import pandas as pd
import datetime as dt
import xarray as xr
from pyclouds import *
from helpers import *

try:
    git_module_version = subprocess.check_output(["git", "describe", "--dirty"]).strip().decode("utf-8")
except:
    git_module_version = "--"


# Read zooniverse raw data
logging.info('Read zooniverse raw data')
subj = zooniverse.load_classifications(subj_fn)
clas = zooniverse.parse_classifications(clas_fn,
                                        json_columns=['metadata', 'annotations', 'subject_data'])

logging.debug('Combine zooniverse subject data and classification data')
data_combined = add_subject_set_id_to_clas_df(clas, subj, subjs_of_interest)

# During development the VIS workflow changed. Select final version only
for workflow_name, df in data_combined.groupby('workflow_id'):
    print(workflow_name, np.unique(df.workflow_version))

# based on aboves overview the following versions will be chosen
version_dict = {13306: [21.18], 13309: [17.12], 13406: [14.16], 13496: [14.11]}
data_combined = restrict_to_version(data_combined, version_dict)

# Make classifications and other data better accessable in the dataframe
# by extracting values from dictionaries
logging.info('Extract classifications from deep data structure')
data_export = convert_clas_to_annos_df(data_combined)

# Extract further metainformation from the filename
# e.g. simulation init time, actual time, satellite
logging.info('Extract metadata from filename')
dates = np.empty(len(data_export),dtype=dt.datetime)
init_dates = np.empty_like(dates)
instruments = np.empty(len(data_export), dtype='object')
for f,fn in enumerate(data_export.fn):
    _dict = decode_filename_eurec4a(fn)
    dates[f] = _dict['date']
    init_dates[f] = _dict['init_date']
    instruments[f] = _dict['instrument']

data_export['date'] = dates
data_export['init_date'] = init_dates
data_export['instrument'] = instruments

# Remove unnecessary data fields
logging.info('Remove unnecessary data fields')
data_export = data_export.drop(columns=['user_ip', 'gold_standard', 'workflow_version',
                                        'expert', 'subject_set_id', 'annotations',
                                        'metadata', 'subject_data'])

# Extract the actual label from the tool description which also included
# thumbnail link
data_export['tool_label'] = data_export.tool_label.apply(clean_tool_label)

# Remove path from filename
data_export['fn'] = data_export.fn.apply(os.path.basename)

# Handling classification overflow (classifications crossing the edges of the image)
# by reseting the coordinates to the allowed boundaries
# also calculating the actual geographical positions
logging.info('Handling classification overflows')
positions = np.zeros((len(data_export),4))
for r,row in data_export.iterrows():
    if 'ICON' in row.workflow_name:
        region = [6]
        imag_dim = (882, 735)
    else:
        region = [5]
        imag_dim = (2200,1500)
    coords_in = (row['x'], row['y'], row['width'], row['height'])
    if not all(coords_in): continue
    row['x'], row['y'], row['width'], row['height'] = limit_classifications_to_domain(coords_in, imag_dim)
    data_export.loc[r, 'x'] = row['x']
    data_export.loc[r, 'y'] = row['y']
    data_export.loc[r, 'width'] = row['width']
    data_export.loc[r, 'height'] = row['height']
    coords = [helpers.wh2xy(np.round(row['x']).astype(int)-1, np.round(row['y']).astype(int)-1,
                            np.round(row['width']).astype(int)-1,np.round(row['height']).astype(int)-1)]
    positions[r,:] = zooniverse.convert_pixelCoords2latlonCoords(coords,region, imag_dimensions=imag_dim)[:,0]

data_export['lon0'] = positions[:,0]
data_export['lat0'] = positions[:,1]
data_export['lon1'] = positions[:,2]
data_export['lat1'] = positions[:,3]

# Export Level1 data
logging.info('Export level1 data to {}'.format(level1_file))
ds_l1 = xr.Dataset.from_dataframe(data_export)
ds_l1.attrs['title'] = 'EUREC4A: manual meso-scale cloud pattern classifications'
ds_l1.attrs['description'] = 'Level-1: restructured enhanced raw data'
ds_l1.attrs['author'] = 'Hauke Schulz (hauke.schulz@mpimet.mpg.de)'
ds_l1.attrs['created_on'] = dt.datetime.now().strftime('%Y-%m-%d %H:%M UTC')
ds_l1.attrs['created_with'] = os.path.basename(__file__) + " with its last modification on " + time.ctime(
            os.path.getmtime(os.path.realpath(__file__)))
ds_l1.attrs['version'] = git_module_version
ds_l1.attrs['python_version'] = "{}".format(sys.version)
ds_l1.attrs['doi'] = 'not yet set'

ds_l1.subject_ids.attrs['description'] = 'Identifier to which subject set the image belongs to'
ds_l1.fn.attrs['description'] = 'Filename of source image file'
ds_l1.x.attrs['description'] = 'x-origin of label'
ds_l1.y.attrs['description'] = 'y-origin of label'
ds_l1.width.attrs['description'] = 'width of label'
ds_l1.height.attrs['description'] = 'height of label'
ds_l1.tool_label.attrs['description'] = 'label'
ds_l1.already_seen.attrs['description'] = 'Flag wheather the user has seen the label already'

ds_l1['already_seen'] = ds_l1.already_seen.astype(bool)

ds_l1.to_netcdf(level1_file)
