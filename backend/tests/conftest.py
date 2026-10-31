import sys
from pathlib import Path

# S'assure que le dossier 'src' est présent dans sys.path
src_dir = Path(__file__).resolve().parent.parent / "src"
if str(src_dir) not in sys.path:
    sys.path.insert(0, str(src_dir))

