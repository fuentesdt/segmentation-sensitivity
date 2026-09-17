"""Shared paths; override through environment variables before running."""
from pathlib import Path
import os

ROOT = Path(__file__).resolve().parent.parent
WORK = Path(os.environ.get('STUDY_WORK', '/scratch/pzz1/segmentation-sensitivity' if Path('/scratch/pzz1').exists() else str(ROOT / '.work')))
RESULTS = ROOT / 'results'
ARCHIVE = Path(os.environ.get('STUDY_DATA_ZIP', '/projects/br1/pzz1/segmentation-sensitivity/oilblooddata.zip'))
