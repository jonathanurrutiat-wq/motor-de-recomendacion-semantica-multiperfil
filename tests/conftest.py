import sys
from pathlib import Path

# Los módulos se importan como src.<modulo>, igual que desde src/main.py.
RAIZ = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(RAIZ))
