#!/bin/bash
# Runs the CaliPro driver. It only samples, submits each iteration's job array,
# waits, and refines ranges.
#   sbatch calipro_driver_job.sh        (from the CaliPro repo root)
#SBATCH --job-name=calipro_driver
#SBATCH --account=def-nicoleli
#SBATCH --cpus-per-task=1
#SBATCH --mem=8G
#SBATCH --time=24:00:00                 # whole calibration, incl. queue waits
#SBATCH --output=/dev/null
set -euo pipefail

# this attempt's folder named by job ID, where all further output gets sent
export CALIPRO_OUT_DIR="output/Calibration_job${SLURM_JOB_ID}"
mkdir -p "$CALIPRO_OUT_DIR"
exec > "$CALIPRO_OUT_DIR/driver.log" 2>&1
echo "CaliPro driver job $SLURM_JOB_ID started $(date)"

module load StdEnv/2023 gcc/12.3 python/3.11
chmod +x bin/testRun

source "$HOME/calipro_env/bin/activate"

python -u calibration_driver.py

echo "Finished $(date)"
