#!/usr/bin/env bash
#SBATCH --job-name=seg-mpi-check
#SBATCH --account=commons
#SBATCH --partition=commons
#SBATCH --qos=nots_commons
#SBATCH --nodes=1
#SBATCH --ntasks=2
#SBATCH --cpus-per-task=1
#SBATCH --mem=16G
#SBATCH --time=00:30:00
#SBATCH --output=validation-mpi-%j.log
set -euo pipefail
cd "${STUDY_ROOT:-${SLURM_SUBMIT_DIR:?Submit from the repository root}}"
source src/environment.sh
mpirun -n 1 python -u -m src.run --geometry toys --n 8 --cases gap_at_0.5,gap_trunk,gap_upper --output ${STUDY_WORK}/validation/mpi1
mpirun -n 2 python -u -m src.run --geometry toys --n 8 --output ${STUDY_WORK}/validation/mpi2
mpirun -n 1 python -u -m src.run --geometry toys --n 8 --inlet 2 --cases gap_at_0.5,gap_trunk,gap_upper --output ${STUDY_WORK}/validation/amplitude2
