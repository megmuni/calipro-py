#!/bin/bash
# One CaliPro ABM run per array task. Submitted by model_run.py, not by hand:
#   sbatch --wait --array=0-N%cap --output=<iter dir>/slurm_%a.out calipro_array_job.sh <iter dir>
#SBATCH --job-name=calipro_run
#SBATCH --account=rrg-nicoleli          # EDIT: your allocation
#SBATCH --gpus=h100_1g.10gb:1
#SBATCH --cpus-per-task=2
#SBATCH --mem=16G                        # EDIT if the ABM needs more
#SBATCH --time=00:20:00                 # EDIT: comfortably above one run's time
set -euo pipefail

module load StdEnv/2023 gcc/12.3 python/3.11
source "$HOME/calipro_env/bin/activate"

# ABM needs GPU so this line will fail the job if the task didn't get one
nvidia-smi -L > /dev/null || { echo "No GPU visible in task $SLURM_ARRAY_TASK_ID"; exit 1; }

python -m calipro.run_task "$1" "$SLURM_ARRAY_TASK_ID"
