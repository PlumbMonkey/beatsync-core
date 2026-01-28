
from pathlib import Path
import sys

REPO = Path(__file__).resolve().parents[1]
ADDON_DIR = REPO / "addon"
if str(ADDON_DIR) not in sys.path:
	sys.path.insert(0, str(ADDON_DIR))
