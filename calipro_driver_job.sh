#!/bin/bash
# Runs the CaliPro driver. It only samples, submits each iteration's job array,
# waits, and refines ranges.
#   sbatch calipro_driver_job.sh        (from the CaliPro repo root)
#SBATCH --job-name=calipro_driver
#SBATCH --account=def-nicoleli
#SBATCH --cpus-per-task=1
#SBATCH --mem=8G
#SBATCH --time=24:00:00                 # whole calibration, incl. queue waits
set -euo pipefail

module load StdEnv/2023 gcc/12.3 python/3.11

source "$HOME/calipro_env/bin/activate"

python calibration_driver.py
