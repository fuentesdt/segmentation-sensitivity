#!/usr/bin/env bash
#SBATCH --job-name=seg-large-check
#SBATCH --account=commons
#SBATCH --partition=commons
#SBATCH --qos=nots_commons
#SBATCH --nodes=1
#SBATCH --ntasks=4
#SBATCH --cpus-per-task=1
#SBATCH --mem=32G
#SBATCH --time=01:00:00
#SBATCH --output=large-validation-%j.log
set -euo pipefail
cd "${STUDY_ROOT:-${SLURM_SUBMIT_DIR:?Submit from the repository root}}"
source src/environment.sh
mpirun -n 4 python -u -m src.run --geometry tree --n 32 --cases seed_11_breaks_8,seed_11_breaks_32 --output ${STUDY_WORK}/validation/large_mesh
mpirun -n 4 python -u -m src.run --geometry tree --n 48 --cases seed_11_breaks_8,seed_11_breaks_32 --output ${STUDY_WORK}/validation/large_mesh
