"""Small helper to run the project directly without installing it."""
import sys
from pathlib import Path
def ensure_src_path():
    sys.path.insert(0, str(Path(__file__).resolve().parent / "src"))
