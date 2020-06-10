# EUREC4A_manualclassifications
[![DOI](https://zenodo.org/badge/DOI/10.5281/zenodo.3763414.svg)](https://doi.org/10.5281/zenodo.3763414)

This repository includes the source code for the post-processing of the manual cloud classifications
that have been gathered during an online hackathon with international scientists in March 2020.

## Example usage: get meso-scale organization along trajectory
One of the use cases of this dataset is to retrieve the meso-scale organization of shallow convection
at a specific point in time and space. Because the variety and number of platforms during the EUREC4A
campaign has been enormous, the procedure to retrieve the cloud classifications along a trajectory is
shown below for the RV Meteor.
<details><summary>Source code</summary>

```python
import numpy as np
import xarray as xr
import matplotlib.pyplot as plt
from matplotlib import dates
import datetime as dt
from pandas.plotting import register_matplotlib_converters
register_matplotlib_converters()
```
Choose a specific workflow e.g. IR or VIS
```python
# Workflow as given in l3 output
workflow = 'IR'

# Level3 filename (input)
level3_file = '../processed_data/EUREC4A_ManualClassifications_l3_{workflow}.zarr'.format(workflow=workflow)

# DSHIP Meteor (input)
meteor_dship_file = 'EUREC4A_Meteor_DSHIP.nc'
```

Open `level 3` dataset:
```python
ds = xr.open_zarr(level3_file)
```

Define standard colors:
```python
color_dict = {'Flowers':'#2281BB',
              'Fish': '#93D2E2',
              'Gravel': '#3EAE47',
              'Sugar': '#A1D791'}
```

Open the trajectory file of the platform of interest.
(How to retrieve the Meteor data is explained e.g. at [DSHIPConverter](https://github.com/observingClouds/DSHIPconverter))
```python
ds_meteor = xr.open_dataset(meteor_dship_file)

# Make coordinates data variables
ds_meteor['latitude'] = xr.DataArray(ds_meteor.lat.values, dims=['time'])
ds_meteor['longitude'] = xr.DataArray(ds_meteor.lon.values, dims=['time'])
```
The `level 3` data is a daily average. For simplicity, we calculate the daily mean position of the vessel:
```python
ds_meteor_daily = ds_meteor.resample(time='1D').mean() # Attention, only works as long as the 0 meridian is not crossed
```

Load and plot the data:
```python
frequency = np.zeros((len(ds.date)))

fig, ax = plt.subplots(figsize=(8,1.5))

for d, date in enumerate(ds_meteor_daily.time):
    frequency = 0
    lat = ds_meteor_daily.latitude.sel(time=date)
    lon = ds_meteor_daily.longitude.sel(time=date)
    for p in ['Sugar', 'Gravel', 'Fish', 'Flowers']:
        try:
            # Actually loading the data
            data = ds.freq.interp(latitude=lat, longitude=lon).sel(date=date, pattern=p).values *100
        except KeyError:
            print('No data found for date {}'.format(date))
            break
        if np.isnan(data):
            data = 0
        ax.bar(dates.date2num(date), data, label=p, bottom=frequency, color=color_dict[p])
        hfmt = dates.DateFormatter('%d.%m')
        ax.xaxis.set_major_locator(dates.DayLocator(interval=5))
        ax.xaxis.set_major_formatter(hfmt)
        frequency += data
    if d == 0:
        plt.legend(frameon=False, bbox_to_anchor=(1,1))
plt.xlabel('date')
plt.ylabel('classification (%)')
plt.xlim(dt.datetime(2020,1,6), dt.datetime(2020,2,23))
```
</details>

![timeseries](https://github.com/observingClouds/EUREC4A_manualclassifications/blob/master/figures/ManualClassification_Meteor_IR.png?raw=true)
