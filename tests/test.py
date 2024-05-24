import sys
from pathlib import Path

src = str((Path(__file__).parent / "../src").resolve())
sys.path.insert(0, src)
