# Create zip file for zenodo data upload

## Anonymize raw data
python anonymize_data.py

## Zip data
cd ../

mkdir zenodo

zip -r -D zenodo/EUREC4A_ManualCloudClassificationData.zip processed_data/EUREC4A_ManualClassifications_l2.zarr processed_data/EUREC4A_ManualClassifications_l3_VIS_instant.zarr processed_data/EUREC4A_ManualClassifications_l3_VIS_daily.zarr processed_data/EUREC4A_ManualClassifications_l3_IR_instant.zarr processed_data/EUREC4A_ManualClassifications_l3_IR_daily.zarr processed_data/EUREC4A_ManualClassifications_l3_albedo_instant.zarr processed_data/EUREC4A_ManualClassifications_l3_albedo_daily.zarr processed_data/EUREC4A_ManualClassifications_l1_anonymized.nc zooniverse_raw/sugar-flower-fish-or-gravel-subjects.csv zooniverse_raw/sugar-flower-fish-or-gravel-classifications_anonymized.csv

