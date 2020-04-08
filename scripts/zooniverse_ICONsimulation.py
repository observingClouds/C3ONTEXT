"""
Script to plot ICON simulations in preparation
to upload to zooniverse.
"""

import datetime as dt
import os
import glob
import tqdm
import numpy as np
import xarray as xr
import matplotlib.pyplot as plt

path_to_simulations_fmt = '/work/bb1156/ICON-1.25km/DATA/*/dei4_*2d_ll_DOM01_ML_*.nc'
lat0, lat1, lon0, lon1 = 5, 20 , -62, -40
output_filename_fmt = 'EUREC4A_ICON_{var}_{init_date}_%Y%m%d%H%M.jpeg'
output_dpi = 199  # 497: 100px per 1 deg ~ 1km resolution; 199: 2.5km resolution
variable = 'tqci'  # tqci or albedo

def retrieve_infos_from_filename(filename):
    """
    Retrieve metadata from filename :(
    """
    metadata = {}
    bn = os.path.basename(filename)
    bn_parts = bn.split('_')
    metadata['init_date'] = dt.datetime.strptime(bn_parts[2], '%Y%m%d%H')
    metadata['sim_time'] = np.int(bn_parts[7][:-3])
    metadata['actual_time'] = metadata['init_date'] + dt.timedelta(hours=metadata['sim_time'])
    return metadata


def albedo(lwp, nc=70):
    """
    Calculate albedo

    Input
    -----
    lwp : array
        Liquid water vapor path
    nc : array or float
        Cloud droplet number density (cm3)
    """
    tau = 0.19 * (lwp**(5/6)) * (nc**(1/3))
    return tau/(6.8+tau)

files = sorted(glob.glob(path_to_simulations_fmt))

for file in tqdm.tqdm(files):
    metadata = retrieve_infos_from_filename(file)
    if (metadata['sim_time'] < 24) or (metadata['sim_time'] ==48): continue  # don't use initialization time
    time = metadata['actual_time']

    ds_sim = xr.open_dataset(file)

    plt.figure(dpi=200)

    if variable == 'tqci':
        tqc = ds_sim.isel({'time':0, 'height':0}).sel({'lat':slice(lat0, lat1), 'lon':slice(lon0, lon1)}).tqc_dia.values
        tqi = ds_sim.isel({'time':0, 'height':0}).sel({'lat':slice(lat0, lat1), 'lon':slice(lon0, lon1)}).tqi_dia.values
        tqi[tqi<=0] = np.nan
        plt.imshow(tqc, cmap='RdBu_r', vmax=1, vmin=0, origin='lower', aspect=1)
        plt.imshow(tqi, cmap='Blues', alpha=0.4, origin='lower', aspect=1)
    elif variable == 'albedo':
        tqc = ds_sim.isel({'time':0, 'height':0}).sel({'lat':slice(lat0, lat1), 'lon':slice(lon0, lon1)}).tqc_dia.values
        a = albedo(tqc*1000, nc=70)
        plt.imshow(a, cmap='bone', origin='lower', aspect=1)
    plt.gca().set_aspect('equal')
    plt.axis('off');
    output_filename = output_filename_fmt.format(var=variable, init_date=metadata['init_date'].strftime('%Y%m%d%H'))
    plt.savefig(time.strftime(output_filename), bbox_inches='tight', pad_inches=0, dpi=199)
    plt.close()
