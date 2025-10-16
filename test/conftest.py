import sys
from pathlib import Path

# Ensure the repository root is on sys.path so tests can import `src`.
REPO_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO_ROOT))
