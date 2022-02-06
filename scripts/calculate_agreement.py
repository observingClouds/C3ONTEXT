"""
Calculation of agreement between different classification
approaches.
"""

domain = [10, 24, -61, -40]  # domain of original data [lat1, lat2, lon1, lon2]
lat0, lat1, lon0, lon1 = [10, 20, -58, -48]
label_map= {'Sugar':0, 'Fish': 3, 'Flowers': 2, 'Flower': 2, 'Gravel': 1}
label_map_rv = {0:'Sugar', 1:'Gravel', 2: 'Flowers', 3: 'Fish'}
color_dict = {'Sugar':'#A1D791','Fish':'#2281BB','Gravel':'#3EAE47', 'Flowers': '#93D2E2'}

fn_ABI_IR = '../auxiliary_data/GOES16_CH13_classifications_EUREC4A_30min.zarr/'
files_manualClassifications_l3 = {
       "manualVIS": '../processed_data/EUREC4A_ManualClassifications_l3_VIS_instant.zarr',
       "manualIR": '../processed_data/EUREC4A_ManualClassifications_l3_IR_instant.zarr',
       "manualICON": '../processed_data/EUREC4A_ManualClassifications_l3_albedo_instant.zarr' 
}
fn_iorg = '../auxiliary_data/GOES16_IR_nc_Iorg_EUREC4A_10-20_-58--48.nc'

import tqdm
import dask
import zarr
import xarray as xr
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.patches import Circle, Wedge, Polygon
from matplotlib.collections import PatchCollection
import datetime as dt
import pandas as pd

import sys, os
sys.path.append("/home/mpim/m300408/CloudClassification/sugar-flower-fish-or-gravel")
sys.path.remove(os.path.abspath(os.path.dirname(sys.argv[0])))
from pyclouds.imports import *
from pyclouds.helpers import *
from pyclouds.zooniverse import *
from pyclouds.plot import *

import pyclouds
print(pyclouds.__file__)

del tqdm
import tqdm

sys.path.append("../notebooks/")
import glob
from agreement_helpers import *

import argparse
import logging

logging.info(f"pandas version: {pd.__version__}")

def get_args():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('-t', '--threshold', help='Agreement threshold', required=False, default=0.1)

    args = vars(parser.parse_args())

    return args


args = get_args()
frequency_threshold = float(args["threshold"])

### Open neural network classifications
mask_ABI_IR = xr.open_zarr(fn_ABI_IR)

for workflow, l3_file in sorted(files_manualClassifications_l3.items()):
    ### Open manual classifications
    if '.zarr' in l3_file:
        mask_manual_classifications = xr.open_zarr(l3_file)
    elif '.nc' in l3_file:
        mask_manual_classifications = xr.open_dataset(l3_file)
    else:
        logging.error('File format not supported')
    
    # find common times
    time_set_A = set(mask_ABI_IR.time.dt.floor(freq='1T').values)
    time_set_B = set(mask_manual_classifications.date.values)
    common_dates = np.array([*time_set_A.intersection(time_set_B)])
    times_of_interest = sorted(np.unique(common_dates))

    time_mask_ABIIR = np.in1d(mask_ABI_IR.time.dt.floor(freq='1T').values,common_dates)

    mask_ABI_IR_timesel = mask_ABI_IR.sel(time=time_mask_ABIIR)
    mask_ABI_IR_timesel['date'] = mask_ABI_IR_timesel.time.dt.floor(freq='1T')

    mask_manual_timesel = mask_manual_classifications.sel(date=common_dates)

    results = {}

    logging.info("Find common times to all datasets")
    sizes_calculated = False

    for ii, i in enumerate(tqdm.tqdm(range(len(times_of_interest)))):
        mask_ABI_IR_timestep = mask_ABI_IR_timesel.where(mask_ABI_IR_timesel.date == times_of_interest[i], drop=True)
        mask_manual_timestep = mask_manual_timesel.sel(date=times_of_interest[i])



        mask_ABI_IR_timestep = mask_ABI_IR_timestep.sel(latitude=slice(lat1, lat0),longitude=slice(lon0, lon1))
        mask_manual_timestep = mask_manual_timestep.sel(latitude=slice(lat1, lat0),longitude=slice(lon0, lon1))

        if sizes_calculated is False:
            size_ABI = len(mask_ABI_IR_timestep.latitude)*len(mask_ABI_IR_timestep.longitude)
            size_manual = len(mask_manual_timestep.latitude)*len(mask_manual_timestep.longitude)
            sizes_calculated = True

        pattern_results = {}

        for p, pattern in enumerate(['Sugar', 'Gravel', 'Flowers', 'Fish']):
            pattern_results[pattern] = {}
            if pattern != 'Unclassified':
                # there is no unclassified category in the neural network classifications
                arr_ABI = mask_ABI_IR_timestep.mask.sel(pattern=pattern)
                merged_mask_ABI = merge_mask(arr_ABI)
                merged_mask_ABI = merged_mask_ABI.fillna(False).astype(bool).load()
                pattern_results[pattern]["area_fraction_ABI"] = np.count_nonzero(merged_mask_ABI)/size_ABI

                if p == 0:
                    total_classification_mask_ABI = merged_mask_ABI
                else:
                    total_classification_mask_ABI += merged_mask_ABI

            arr_manual = mask_manual_timestep.freq.sel(pattern=pattern)
            merged_mask_manual = arr_manual > frequency_threshold
            merged_mask_manual = merged_mask_manual.load()
            pattern_results[pattern][f"area_fraction_{workflow}"] = np.count_nonzero(merged_mask_manual)/size_manual

            if p == 0:
                total_classification_mask = merged_mask_manual
            else:
                total_classification_mask += merged_mask_manual

            if pattern != 'Unclassified':
                iou_ABI_Manual = iou_one_class_from_annos(merged_mask_ABI.values,
                                                        merged_mask_manual.values,
                                                        return_iou = True)

                pattern_results[pattern][f"iou_ABI_{workflow}"] = iou_ABI_Manual
                pattern_results[pattern][f"missing_ABI_{workflow}"] = identify_where_class_missing(merged_mask_ABI,
                                                                                            merged_mask_manual)

        pattern_results['Unclassified'] = {f"area_fraction_{workflow}":np.count_nonzero(~total_classification_mask)/size_manual,
                                           "area_fraction_ABI":np.count_nonzero(~total_classification_mask_ABI)/size_manual
                                          }
        results[times_of_interest[i]] = pattern_results
    df = pd.DataFrame.from_dict(results, orient='index')
    output_folder = f'../temporary_data/agreement_threshold{frequency_threshold}'
    if not os.path.exists(output_folder):
        os.makedirs(output_folder)
    df.to_pickle(output_folder+f'/agreement_results_ABI-IR_vs_{workflow}.pkl')
