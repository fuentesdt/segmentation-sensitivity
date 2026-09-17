#!/usr/bin/env bash
#SBATCH --job-name=seg-validation
#SBATCH --account=commons
#SBATCH --partition=commons
#SBATCH --qos=nots_commons
#SBATCH --nodes=1
#SBATCH --ntasks=4
#SBATCH --cpus-per-task=1
#SBATCH --mem=24G
#SBATCH --time=01:00:00
#SBATCH --output=validation-%j.log
set -euo pipefail
cd "${STUDY_ROOT:-${SLURM_SUBMIT_DIR:?Submit from the repository root}}"
source src/environment.sh
mpirun -n 4 python -u -m src.validate
mpirun -n 4 python -u -m src.run --geometry toys --n 12 --cases gap_at_0.5,gap_trunk,gap_upper --output ${STUDY_WORK}/validation/mesh
mpirun -n 4 python -u -m src.run --geometry toys --n 36 --cases gap_at_0.5,gap_trunk,gap_upper --output ${STUDY_WORK}/validation/mesh
mpirun -n 4 python -u -m src.run --geometry toys --n 24 --h .005 --cases gap_at_0.5,gap_trunk,gap_upper --output ${STUDY_WORK}/validation/network_refinement
mpirun -n 4 python -u -m src.run --geometry toys --n 24 --circle-degree 40 --cases gap_at_0.5,gap_trunk,gap_upper --output ${STUDY_WORK}/validation/quadrature
