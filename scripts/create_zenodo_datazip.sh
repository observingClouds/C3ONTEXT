# Create zip file for zenodo data upload

## Anonymize raw data
python anonymize_data.py

## Zip data
cd ../processed_data/

zip -r -D -j ../zenodo/EUREC4A_ManualCloudClassificationData.zip EUREC4A_ManualClassifications_l2.zarr EUREC4A_ManualClassifications_l3_VIS.zarr EUREC4A_ManualClassifications_l3_IR.zarr EUREC4A_ManualClassifications_l3_ICON.zarr EUREC4A_ManualClassifications_l1_anonymized.nc ../zooniverse_raw/sugar-flower-fish-or-gravel-subjects.csv ../zooniverse_raw/sugar-flower-fish-or-gravel-classifications_anonymized.csv

