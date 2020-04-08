import sys, os
import image_download as worldview
from datetime import datetime as date
from pandas import date_range

# Load configuration
from subprocess import check_output


verbose = True
skip_existing = True
output_path_fmt = "./CHANNEL/SUBDIR/"

download_configs = [
	# MODIS IR images region1
	# {'channel':'VIS', 'satellite':'GOES', 'var':'GOES-East_ABI_Band2_Red_Visible_1km', 'dates':date_range(date(2020,1,1), date(2020,1,10), freq="1H"), 'lon_range':[-62, -40], 'lat_range':[5, 20], 'subdir':'EUREC4A_GOES_C02'},
	{'channel':'VIS', 'satellite':'Aqua', 'var':'MODIS_Aqua_CorrectedReflectance_TrueColor', 'dates':date_range(date(2020,1,7), date(2020,2,22), freq="1D"), 'lon_range':[-62, -40], 'lat_range':[5, 20], 'subdir':'EUREC4A_MODIS_AQUA-VIS'},
	{'channel':'VIS', 'satellite':'Terra', 'var':'MODIS_Terra_CorrectedReflectance_TrueColor', 'dates':date_range(date(2020,1,7), date(2020,2,22), freq="1D"), 'lon_range':[-62, -40], 'lat_range':[5, 20], 'subdir':'EUREC4A_MODIS_TERRA-VIS'}
	# {'channel':'IR', 'satellite':'Terra', 'var':'Brightness_Temp_Band31_Day', 'years':[2007,2018], 'months':[3,4,5], 'lon_range':[-61,-40], 'lat_range':[10,24], 'subdir':'Region1_MAM_Terra'},
	# {'channel':'IR', 'satellite':'Aqua', 'var':'Brightness_Temp_Band31_Day', 'years':[2007,2018], 'months':[12,1,2], 'lon_range':[-61,-40], 'lat_range':[10,24], 'subdir':'Region1_DJF_Aqua'},
	# {'channel':'IR', 'satellite':'Aqua', 'var':'Brightness_Temp_Band31_Day', 'years':[2007,2018], 'months':[3,4,5], 'lon_range':[-61,-40], 'lat_range':[10,24], 'subdir':'Region1_MAM_Aqua'},
	# # MODIS VIS images region1
	# {'channel':'VIS', 'satellite':'Terra', 'var':'CorrectedReflectance', 'years':[2007,2018], 'months':[12,1,2], 'lon_range':[-61,-40], 'lat_range':[10,24], 'subdir':'Region1_DJF_Terra'},
	# {'channel':'VIS', 'satellite':'Terra', 'var':'CorrectedReflectance', 'years':[2007,2018], 'months':[3,4,5], 'lon_range':[-61,-40], 'lat_range':[10,24], 'subdir':'Region1_MAM_Terra'},
	# {'channel':'VIS', 'satellite':'Aqua', 'var':'CorrectedReflectance', 'years':[2007,2018], 'months':[12,1,2], 'lon_range':[-61,-40], 'lat_range':[10,24], 'subdir':'Region1_DJF_Aqua'},
	# {'channel':'VIS', 'satellite':'Aqua', 'var':'CorrectedReflectance', 'years':[2007,2018], 'months':[3,4,5], 'lon_range':[-61,-40], 'lat_range':[10,24], 'subdir':'Region1_MAM_Aqua'},

	# # MODIS IR images region2
	# {'channel':'IR', 'satellite':'Terra', 'var':'Brightness_Temp_Band31_Day', 'years':[2007,2018], 'months':[12,1,2], 'lon_range':[159,180], 'lat_range':[8,22], 'subdir':'Region2_DJF_Terra'},
	# {'channel':'IR', 'satellite':'Aqua', 'var':'Brightness_Temp_Band31_Day', 'years':[2007,2018], 'months':[12,1,2], 'lon_range':[159,180], 'lat_range':[8,22], 'subdir':'Region2_DJF_Aqua'},
	# # MODIS VIS images region2
	# {'channel':'VIS', 'satellite':'Terra', 'var':'CorrectedReflectance', 'years':[2007,2018], 'months':[12,1,2], 'lon_range':[159,180], 'lat_range':[8,22], 'subdir':'Region2_DJF_Terra'},
	# {'channel':'VIS', 'satellite':'Aqua', 'var':'CorrectedReflectance', 'years':[2007,2018], 'months':[12,1,2], 'lon_range':[159,180], 'lat_range':[8,22], 'subdir':'Region2_DJF_Aqua'},

	# # MODIS IR images region3
	# {'channel':'IR', 'satellite':'Terra', 'var':'Brightness_Temp_Band31_Day', 'years':[2007,2018], 'months':[12,1,2], 'lon_range':[-135,-114], 'lat_range':[-15,-1], 'subdir':'Region3_DJF_Terra'},
	# {'channel':'IR', 'satellite':'Terra', 'var':'Brightness_Temp_Band31_Day', 'years':[2007,2018], 'months':[9,10,11], 'lon_range':[-135,-114], 'lat_range':[-15,-1], 'subdir':'Region3_SON_Terra'},
	# {'channel':'IR', 'satellite':'Aqua', 'var':'Brightness_Temp_Band31_Day', 'years':[2007,2018], 'months':[12,1,2], 'lon_range':[-135,-114], 'lat_range':[-15,-1], 'subdir':'Region3_DJF_Aqua'},
	# {'channel':'IR', 'satellite':'Aqua', 'var':'Brightness_Temp_Band31_Day', 'years':[2007,2018], 'months':[9,10,11], 'lon_range':[-135,-114], 'lat_range':[-15,-1], 'subdir':'Region3_SON_Aqua'},
	# # MODIS VIS images region3
	# {'channel':'VIS', 'satellite':'Terra', 'var':'CorrectedReflectance', 'years':[2007,2018], 'months':[12,1,2], 'lon_range':[-135,-114], 'lat_range':[-15,-1], 'subdir':'Region3_DJF_Terra'},
	# {'channel':'VIS', 'satellite':'Terra', 'var':'CorrectedReflectance', 'years':[2007,2018], 'months':[3,4,5], 'lon_range':[-135,-114], 'lat_range':[-15,-1], 'subdir':'Region3_MAM_Terra'},
	# {'channel':'VIS', 'satellite':'Aqua', 'var':'CorrectedReflectance', 'years':[2007,2018], 'months':[12,1,2], 'lon_range':[-135,-114], 'lat_range':[-15,-1], 'subdir':'Region3_DJF_Aqua'},
	# {'channel':'VIS', 'satellite':'Aqua', 'var':'CorrectedReflectance', 'years':[2007,2018], 'months':[3,4,5], 'lon_range':[-135,-114], 'lat_range':[-15,-1], 'subdir':'Region3_MAM_Aqua'}
]
import pdb; pdb.set_trace()

for cfg in download_configs:
	# Create output from output format
	# (filename is created within download function)
	output_path = output_path_fmt.replace('CHANNEL',cfg['channel'])
	output_path = output_path.replace('SUBDIR',cfg['subdir'])
	output_path = os.path.expanduser(output_path)
	worldview.download_geostationary_imgs(dates=cfg['dates'], save_path=output_path,\
		lon_range=cfg['lon_range'], lat_range=cfg['lat_range'], satellite=cfg['satellite'], exist_skip=skip_existing, var=cfg['var'])
	# worldview.download_MODIS_imgs(year_range=cfg['years'], months=cfg['months'], save_path=output_path,\
	#	 lon_range=cfg['lon_range'], lat_range=cfg['lat_range'], satellite=cfg['satellite'], exist_skip=skip_existing, var=cfg['var'])
