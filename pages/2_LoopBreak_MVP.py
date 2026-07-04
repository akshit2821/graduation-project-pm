"""LoopBreak MVP — submission page."""

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "part-4-mvp"))
sys.path.insert(0, str(ROOT))

from app import main  # noqa: E402

main()
