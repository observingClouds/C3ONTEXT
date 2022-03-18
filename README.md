# C³ONTEXT: A Common Consensus on Convective OrgaNizaTion during the EUREC⁴A eXperimenT
[![Paper](https://img.shields.io/badge/Paper-10.5194%2Fessd--14--1233--2022-green)](https://doi.org/10.5194/essd-14-1233-2022)
[![Data](https://img.shields.io/badge/Data-10.5281%2Fzenodo.3763351-green)](https://doi.org/10.5281/zenodo.3763351)



This repository includes the source code for the post-processing of the manual cloud classifications
that have been gathered during an online hackathon with international scientists in March 2020.

The [overview of the classifications](classification_overview.md) during the EUREC<sup>4</sup>A field campaign gives a good first impression about the dataset and the meso-scale patterns of shallow convection encountered during January - February 2020.

## Example usage: get meso-scale organization along trajectory
One of the use cases of this dataset is to retrieve the meso-scale organization of shallow convection
at a specific point in time and space. Because the variety and number of platforms during the EUREC<sup>4</sup>A
campaign has been enormous, the procedure to retrieve the cloud classifications along a trajectory is
shown below for the RV Meteor.
<details><summary>Source code</summary>

Please install all requirements before executing the code:

```bash
pip install eurec4a dask matplotlib pandas
```

```python
import numpy as np
import datetime as dt
import dask
import matplotlib.pyplot as plt
import eurec4a
from matplotlib import dates
from pandas.plotting import register_matplotlib_converters
register_matplotlib_converters()

cat = eurec4a.get_intake_catalog()
```

Loading classifications that are based on the infrared satellite images.
```python
ds = c3ontext_cat.level3_IR_daily.to_dask()
```

Loading the platform track
```python
platform = 'Meteor'
ds_plat = cat[platform].track.to_dask()
```

Define standard colors:
```python
color_dict = {'Flowers':'#2281BB',
              'Fish': '#93D2E2',
              'Gravel': '#3EAE47',
              'Sugar': '#A1D791'}
```


The `level 3` data used in this example is a daily average. For simplicity and assuming
that both the platform as well as the meso-scale patterns do not change quickly, we calculate the
daily mean position of the platform:
```python
ds_plat_rs = ds_plat.resample(time='1D').mean() # Attention, only works as long as the 0 meridian is not crossed
```

Plot the data:
```python
# Reading the actual data
with dask.config.set(**{'array.slicing.split_large_chunks': False}):
    data = ds.freq.interp(latitude=ds_plat_rs.lat, longitude=ds_plat_rs.lon).sel(date=ds_plat_rs.time)
    data.load()
data=data.fillna(0)*100

# Plotting
fig, ax = plt.subplots(figsize=(8,2))
for d, (time, tdata) in enumerate(data.groupby('time')):
    frequency = 0
    for p in ['Sugar', 'Gravel', 'Flowers', 'Fish', 'Unclassified']:
        ax.bar(dates.date2num(time), float(tdata.sel(pattern=p)), label=p, bottom=frequency, color=color_dict[p])
        hfmt = dates.DateFormatter('%d.%m')
        ax.xaxis.set_major_locator(dates.DayLocator(interval=5))
        ax.xaxis.set_major_formatter(hfmt)
        frequency += tdata.sel(pattern=p)
    if d == 0:
        plt.legend(frameon=False, bbox_to_anchor=(1,1))
plt.xlabel('date')
plt.ylabel('agreement / %')
xlim=plt.xlim(dt.datetime(2020,1,6), dt.datetime(2020,2,23))
```
</details>

![timeseries](https://github.com/observingClouds/EUREC4A_manualclassifications/blob/master/figures/ManualClassification_Meteor_IR_daily.png?raw=true)

Further information on how to use this dataset can also be found on the [How to EUREC⁴A-Website](https://howto.eurec4a.eu/c3ontext.html)
