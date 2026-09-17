#!/usr/bin/env bash
#SBATCH --job-name=seg-results
#SBATCH --account=commons
#SBATCH --partition=commons
#SBATCH --qos=nots_commons
#SBATCH --nodes=1
#SBATCH --ntasks=1
#SBATCH --cpus-per-task=1
#SBATCH --mem=8G
#SBATCH --time=00:20:00
#SBATCH --output=postprocess-%j.log
set -euo pipefail
cd "${STUDY_ROOT:-${SLURM_SUBMIT_DIR:?Submit from the repository root}}"
source src/environment.sh
if [[ -n ${1:-} ]]; then
    sacct --jobs "$1" --parsable2 --format=JobID,JobName,Partition,Account,State,ExitCode,Elapsed,AllocCPUS,MaxRSS > ${STUDY_WORK}/slurm-accounting.txt
fi
python -m src.analyze
python -m src.report
python -m src.supplied_results
python -m src.collect
python -m src.package
