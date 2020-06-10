# Create zip file for zenodo data upload

## Anonymize raw data
python anonymize_data.py

## Zip data
zip -r -D ../processed_data/EUREC4A_ManualClassifications_MergedClassifications.zarr.zip ../processed_data/EUREC4A_ManualClassifications_MergedClassifications.zarr
zip -r -D ../processed_data/EUREC4A_ManualClassifications_l3_IR.zarr.zip ../processed_data/EUREC4A_ManualClassifications_l3_IR.zarr
zip -r -D ../processed_data/EUREC4A_ManualClassifications_l3_VIS.zarr.zip ../processed_data/EUREC4A_ManualClassifications_l3_VIS.zarr
zip -r -D ../processed_data/EUREC4A_ManualClassifications_l3_albedo.zarr.zip ../processed_data/EUREC4A_ManualClassifications_l3_albedo.zarr

zip -D ../zenodo/EUREC4A_ManualCloudClassificationData.zip ../processed_data/EUREC4A_ManualClassifications_MergedClassifications.zarr.zip ../processed_data/EUREC4A_ManualClassifications_l3_VIS.zarr.zip ../processed_data/EUREC4A_ManualClassifications_l3_IR.zarr.zip ../processed_data/EUREC4A_ManualClassifications_l3_albedo.zarr.zip ../processed_data/EUREC4A_ManualClassifications_l1_anonymized.nc ../zooniverse_raw/sugar-flower-fish-or-gravel-subjects.csv ../zooniverse_raw/sugar-flower-fish-or-gravel-classifications_anonymized.csv
