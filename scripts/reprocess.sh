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
# Reprocessing classification data
#
# call script as
#   bash reprocess.sh BAMS     # for classifications done for Rasp et al. 2020
#   bash reprocess.sh EUREC4A  # for classifications done for Schulz et al. 2021
# or in case of using it with SLURM (SLURM header needs to be adapted to your environment)
#   sbatch reprocess.sh BAMS
#   sbatch reprocess.sh EUREC4A

classification=$1

# Download satellite data
# python download_datdata.py
# python goes16_data_download.py  # see also observingClouds/satdownload

# Create images from model output
# bash run_zooniverse_ICONsimulation.sh

# Upload files to zooniverse platform
# python upload_Files.py

# DO THE ACTUAL CLASSIFICATION WORK

# Download the classifications from the webpage (only project team can do this)
# Save download to /zooniverse_raw
module load python3/2021.01-gcc-9.1.0 # this is specific to the DKRZ mistral cluster

# Create level1 file
#python create_level1.py -e ${classification}

# Anonymize level1 file
#python anonymize_data.py -e ${classification}

# Create level2 file
#python create_level2.py -e ${classification}

# Create level3 files
python create_level3.py -e ${classification} -m instant
python create_level3.py -e ${classification} -m daily

# Prepare data for zenodo upload
bash create_zenodo_datazip.sh ${classification}

