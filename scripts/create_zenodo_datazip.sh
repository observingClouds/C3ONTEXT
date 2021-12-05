# Create zip file for zenodo data upload

classification=$1

## Anonymize raw data
python anonymize_data.py -e $1

## Zip data
cd ../

mkdir -p zenodo

zip -r -D zenodo/${classification}_ManualCloudClassificationData.zip processed_data/${classification}_ManualClassifications_l2.zarr processed_data/${classification}_ManualClassifications_l3_VIS_instant.zarr processed_data/${classification}_ManualClassifications_l3_VIS_daily.zarr processed_data/${classification}_ManualClassifications_l3_IR_instant.zarr processed_data/${classification}_ManualClassifications_l3_IR_daily.zarr processed_data/${classification}_ManualClassifications_l3_albedo_instant.zarr processed_data/${classification}_ManualClassifications_l3_albedo_daily.zarr processed_data/${classification}_ManualClassifications_l1_anonymized.nc zooniverse_raw/${classification}_sugar-flower-fish-or-gravel-subjects.csv zooniverse_raw/${classification}_sugar-flower-fish-or-gravel-classifications_anonymized.csv

