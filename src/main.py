import os
import sys
from pathlib import Path

curr_dir = Path(__file__).resolve().parent
sys.path.append(str(curr_dir))
sys.path.append(str(curr_dir.parent))

# ============ Importaciones proyectadas ============
import profiles as prfs
import src.procesing_profiles as emb
import visuals as vs
from src.db.filtered.filter import main as run_filter
from src.loss.gt_matrix_pipeline import main as run_pipeline
from src.loss.ingest_maestro import main as run_maestro




