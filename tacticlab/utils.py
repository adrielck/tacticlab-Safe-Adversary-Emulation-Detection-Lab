from __future__ import annotations
from pathlib import Path

def project_root() -> Path:
    return Path(__file__).resolve().parent.parent

def ensure_dir(p: Path) -> None:
    p.mkdir(parents=True, exist_ok=True)
