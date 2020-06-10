"""
Script to anonymize the classifications

The user names can be deleted and only user ids
are kept.
"""

import pandas as pd
import xarray as xr

raw_data_filename_input = '../zooniverse_raw/sugar-flower-fish-or-gravel-classifications.csv'
raw_data_filename_output = '../zooniverse_raw/sugar-flower-fish-or-gravel-classifications_anonymized.csv'

level1_data_filename_input = '../processed_data/EUREC4A_ManualClassifications_l1.nc'
level1_data_filename_output = '../processed_data/EUREC4A_ManualClassifications_l1_anonymized.nc'

# Anonymize raw data

df = pd.read_csv(raw_data_filename_input)
df = df.iloc[38003:]  # remove data from other classification days
del df['user_name']
df.to_csv(raw_data_filename_output)

# Anonymize level1 data
ds = xr.open_dataset(level1_data_filename_input)
del ds['user_name']
ds.to_netcdf(level1_data_filename_output)
