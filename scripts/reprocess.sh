#!/bin/bash
#SBATCH --account=mh0010
#SBATCH --job-name=reprocess
#SBATCH --partition=shared
#SBATCH --chdir=/work/mh0010/m300408/EUREC4A_CloudClassification/manual/EUREC4A_manualclassifications/scripts/
#SBATCH --nodes=1
#SBATCH --output=/work/mh0010/m300408/EUREC4A_CloudClassification/manual/EUREC4A_manualclassifications/scripts/logs/LOG.reprocess.%j.o
#SBATCH --error=/work/mh0010/m300408/EUREC4A_CloudClassification/manual/EUREC4A_manualclassifications/scripts/logs/LOG.reprocess.%j.o
#SBATCH --time=12:00:00
#SBATCH --mail-user=hauke.schulz@mpimet.mpg.de
#SBATCH --mail-type=ALL
#=============================================================================
# Reprocessing EUREC4A classification data

# Download satellite data
# python download_datdata.py
# python goes16_data_download.py  # see also observingClouds/satdownload

# Create images from model output
# bash run_zooniverse_ICONsimulation.sh

# Upload files to zooniverse platform
# python upload_Files.py

# DO THE ACTUALLY WORK

# Download the classifications from the webpage (only project team can do this)
# Save download to /zooniverse_raw
module load python3/2021.01-gcc-9.1.0
# Create level1 file
#python create_level1.py -e EUREC4A

# Create level2 file
#python create_level2.py -e EUREC4A

# Create level3 files
python create_level3.py -e EUREC4A -m instant
python create_level3.py -e EUREC4A -m daily

# Prepare data for zenodo upload
bash create_zenodo_datazip.sh
