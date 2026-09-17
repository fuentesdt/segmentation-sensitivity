#!/usr/bin/env bash
#SBATCH --job-name=seg-pt002
#SBATCH --account=commons
#SBATCH --partition=commons
#SBATCH --qos=nots_commons
#SBATCH --nodes=1
#SBATCH --ntasks=4
#SBATCH --cpus-per-task=1
#SBATCH --mem=16G
#SBATCH --time=00:45:00
#SBATCH --output=supplied-%j.log
set -euo pipefail
cd "${STUDY_ROOT:-${SLURM_SUBMIT_DIR:?Submit from the repository root}}"
source src/environment.sh
mpirun -n 1 python -u -m src.run --geometry line --n 8 --cases intact --output ${STUDY_WORK}/validation/import_regression
mpirun -n 4 python -u -m src.supplied --h .005 --name intact
mpirun -n 4 python -u -m src.supplied --h .0025 --name network_refinement
