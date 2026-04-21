import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent


def _ensure_artifacts() -> None:
    artifacts = ROOT / "artifacts"
    if (artifacts / "model.pkl").exists() and (artifacts / "metadata.json").exists():
        return
    subprocess.run(
        [sys.executable, str(ROOT / "train.py")],
        check=True,
        cwd=ROOT,
    )


_ensure_artifacts()
