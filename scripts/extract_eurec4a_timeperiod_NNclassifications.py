"""
Extract EUREC4A timeperiod from infrared neural network classification dataset
"""
import xarray as xr
import numcodecs

import dask
from dask_jobqueue import SLURMCluster
from dask.distributed import Client, LocalCluster, comm
print(dask.__version__)
dask.config.config.get('distributed').get('dashboard').update({'link':'{JUPYTERHUB_SERVICE_PREFIX}/proxy/{port}/status'})
cluster = SLURMCluster(project="mh0010")
client = Client(cluster)


ds=xr.open_zarr("/mnt/lustre02/work/mh0010/m300408/CharacterizationOfMesoscalePatterns/Data/Level_1/GOES16_CH13_classifications_2018-2020_NDJFM_30min.zarr/")

# Select EUREC4A time period
ds=ds.sel(time=slice('2020-01-01','2020-03-01'))

del ds.time.attrs['description']

encoding={
    'mask':{'dtype':bool,'compressor':numcodecs.Blosc("zstd",shuffle=numcodecs.Blosc.BITSHUFFLE)},
    'time':{'dtype':'float64'}
         }

ds['mask'] = (ds.mask.astype(float)>0).astype(bool)
ds['pattern'] = ds.pattern.astype('str')

cluster.scale(10)
ds2.to_zarr("../auxiliary_data/GOES16_CH13_classifications_EUREC4A_30min.zarr", encoding=encoding, consolidated=True)
cluster.scale(0)
