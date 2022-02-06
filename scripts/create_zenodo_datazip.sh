# Create zip file for zenodo data upload

classification=$1

## Anonymize raw data
python anonymize_data.py -e $1

## Zip data
cd ../

mkdir -p zenodo

#zip -r -D zenodo/${classification}_ManualCloudClassificationData.zip processed_data/${classification}_ManualClassifications_l2.zarr processed_data/${classification}_ManualClassifications_l3_VIS_instant.zarr processed_data/${classification}_ManualClassifications_l3_VIS_daily.zarr processed_data/${classification}_ManualClassifications_l3_IR_instant.zarr processed_data/${classification}_ManualClassifications_l3_IR_daily.zarr processed_data/${classification}_ManualClassifications_l3_albedo_instant.zarr processed_data/${classification}_ManualClassifications_l3_albedo_daily.zarr processed_data/${classification}_ManualClassifications_l1_anonymized.nc zooniverse_raw/${classification}_sugar-flower-fish-or-gravel-subjects.csv zooniverse_raw/${classification}_sugar-flower-fish-or-gravel-classifications_anonymized.csv

zip -r -D zenodo/${classification}_ManualCloudClassification_l0.zip zooniverse_raw/${classification}_sugar-flower-fish-or-gravel-subjects.csv zooniverse_raw/${classification}_sugar-flower-fish-or-gravel-classifications_anonymized.csv
zip -r -D zenodo/${classification}_ManualCloudClassification_l1.zip processed_data/${classification}_ManualClassifications_l1_anonymized.nc
zip -r -D zenodo/${classification}_ManualCloudClassification_l2.zip processed_data/${classification}_ManualClassifications_l2.zarr
zip -r -D zenodo/${classification}_ManualCloudClassification_l3_IR_daily.zip processed_data/${classification}_ManualClassifications_l3_IR_daily.zarr
zip -r -D zenodo/${classification}_ManualCloudClassification_l3_IR_instant.zip processed_data/${classification}_ManualClassifications_l3_IR_instant.zarr
zip -r -D zenodo/${classification}_ManualCloudClassification_l3_VIS_daily.zip processed_data/${classification}_ManualClassifications_l3_VIS_daily.zarr
zip -r -D zenodo/${classification}_ManualCloudClassification_l3_VIS_instant.zip processed_data/${classification}_ManualClassifications_l3_VIS_instant.zarr
zip -r -D zenodo/${classification}_ManualCloudClassification_l3_albedo_daily.zip processed_data/${classification}_ManualClassifications_l3_albedo_daily.zarr
zip -r -D zenodo/${classification}_ManualCloudClassification_l3_albedo_instant.zip processed_data/${classification}_ManualClassifications_l3_albedo_instant.zarr

if [ $classification = EUREC4A ]
then
   zip -r -D zenodo/${classification}_AuxiliaryData_NeuralNetworkClassifications.zip auxiliary_data/GOES16_CH13_classifications_EUREC4A_30min.zarr
   zip -r -D zenodo/${classification}_AuxiliaryData_IorgSMetrics.zip auxiliary_data/GOES16_IR_nc_Iorg_EUREC4A_10-20_-58--48.nc
   zip -r -D zenodo/${classification}_SourceImages.zip source_images/*
fi

