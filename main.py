"""Compatibility launcher for running from source checkout."""
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent
SRC = ROOT / "src"
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))

from c_purge_tools.app import main


if __name__ == "__main__":
    main()
