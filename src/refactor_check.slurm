#!/usr/bin/env bash
#SBATCH --job-name=seg-refactor-check
#SBATCH --account=commons
#SBATCH --partition=commons
#SBATCH --qos=nots_commons
#SBATCH --nodes=1
#SBATCH --ntasks=2
#SBATCH --cpus-per-task=1
#SBATCH --mem=8G
#SBATCH --time=00:15:00
#SBATCH --output=refactor-check-%j.log
set -euo pipefail
cd "${STUDY_ROOT:-${SLURM_SUBMIT_DIR:?Submit from the repository root}}"
export STUDY_WORK="$PWD/.work/refactor"
source src/environment.sh
mpirun -n 2 python -u -m src.regression --geometry toys --n 8 --cases gap_at_0.5,gap_trunk,gap_upper
