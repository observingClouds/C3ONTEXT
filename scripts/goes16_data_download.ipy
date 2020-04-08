"""
Script to download GOES16 data from Google Cloud and
remap for the purpose of uploading images to zooniverse
for EUREC4A classifications

Hourly files for January and February 2020

Platform: breeze3.mpimet.mpg.de
Environment: BCOenv

Using Ipython
"""

import datetime as dt
import pandas as 
import tqdm
import glob
import xarray as xr

dates = pd.date_range(dt.datetime(2020,1,7), dt.datetime(2020,2,22))                                                                                                                                                                                                  

# Visible (red channel 02)
for date in dates: 
    date_strr = date.strftime('%Y%m%d') 
    print(date_strr) 
    print(len(date_strr)) 
    command = "download_GOES16.py -k 02 -r 5 20 -62 -40 -d {} -t 1 60 -o '/scratch/local1/m300408/GOES16_Zooniverse/GOES16_C02_%Y%m%d_%H%M.nc'".format(date_strr) 
    %run $command

# IR (channel 13)
for date in dates: 
    date_strr = date.strftime('%Y%m%d') 
    print(date_strr) 
    print(len(date_strr)) 
    command = "download_GOES16.py -k 13 -r 5 20 -62 -40 -d {} -t 1 60 -o '/scratch/local1/m300408/GOES16_Zooniverse/GOES16_C13_%Y%m%d_%H%M.nc'".format(date_strr) 
    %run $command


# Converting data to pngs
# Channel02
files = sorted(glob.glob('./*.nc'))
for file in tqdm.tqdm(files):
    ds = xr.open_dataset(file)
    aspect_ratio = np.abs(np.nanmean(np.gradient(ds.lat.values))/np.nanmean(np.gradient(ds.lon.values)))
    plt.figure(figsize=(8,8))
    try:
        plt.imshow(ds.C13.squeeze(), cmap='RdBu_r', aspect=aspect_ratio, vmin=260, vmax=301)
    except:
        plt.imshow(ds.C02.squeeze(), cmap='binary_r', aspect=aspect_ratio, vmin=-10, vmax=80)
    plt.axis('off');
    plt.savefig(file.replace('.nc', '.jpeg'), bbox_inches='tight', pad_inches=0, dpi=354.9)
    plt.close('all')


# Remove unneccessary files (not information in VIS channel during night)
files = sorted(glob.glob('/Users/haukeschulz/Documents/EUREC4A/EUREC4A_CloudClassification/Images/*C02_2020*.png'))
hours_to_delete = [21,22,23,0,1,2,3,4,5,6,7,8,9,10]
for file in files:
    if np.in1d([int(file[-8:-6])], hours_to_delete):
        !rm $file

