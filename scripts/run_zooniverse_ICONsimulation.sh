#!/bin/bash
#SBATCH -J zooniverse          # Specify job name
#SBATCH -p prepost             # Use partition prepost
#SBATCH --mem-per-cpu=244000     # Specify real memory required per CPU in MegaBytes
#SBATCH -t 12:00:00             # Set a limit on the total run time
#SBATCH -A mh0010              # Charge resources on this project account
#SBATCH -o zooniverse.o%j          # File name for standard output
#SBATCH -e zooniverse.e%j          # File name for standard error output


# Execute a serial program, e.g.
module unload netcdf_c
module load anaconda3
cd /work/mh0010/m300408/CloudClassificationImages
source activate /home/mpim/m300408/conda-envs/field_campaign

python zooniverse_ICONsimulation.py

