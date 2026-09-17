#!/usr/bin/env bash
#SBATCH --job-name=seg-sensitivity
#SBATCH --account=commons
#SBATCH --partition=commons
#SBATCH --qos=nots_commons
#SBATCH --nodes=1
#SBATCH --ntasks=8
#SBATCH --cpus-per-task=1
#SBATCH --mem=32G
#SBATCH --time=02:00:00
#SBATCH --output=study-%j.log
set -euo pipefail
cd "${STUDY_ROOT:-${SLURM_SUBMIT_DIR:?Submit from the repository root}}"
source src/environment.sh
mpirun -n 8 python -u -m src.run --geometry toys --n 8 --cases gap_at_0.5,gap_trunk,gap_upper --output ${STUDY_WORK}/validation/mpi8
mpirun -n 8 python -u -m src.run --geometry toys --n 24
mpirun -n 8 python -u -m src.run --geometry tree --n 40
