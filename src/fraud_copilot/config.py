import os
from dataclasses import dataclass
from pathlib import Path
from dotenv import load_dotenv

ROOT = Path(__file__).resolve().parents[2]
load_dotenv(ROOT / ".env")

@dataclass(frozen=True)
class Settings:
    google_api_key: str = os.getenv("GOOGLE_API_KEY", "")
    gemini_model: str = os.getenv("GEMINI_MODEL", "gemini-2.5-flash")
    data_dir: Path = ROOT / "data"
    evidence_dir: Path = ROOT / "evidence"
    logs_dir: Path = ROOT / "logs"
    index_dir: Path = ROOT / ".index"
    checkpoint_db: Path = ROOT / ".index" / "checkpoints.sqlite"

settings = Settings()
for p in (settings.evidence_dir, settings.logs_dir, settings.index_dir):
    p.mkdir(parents=True, exist_ok=True)
