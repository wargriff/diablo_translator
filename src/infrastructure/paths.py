from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[2]
USER_DATA_DIR = PROJECT_ROOT / "user_data"
LOGS_DIR = PROJECT_ROOT / "logs"
EXPORTS_DIR = USER_DATA_DIR / "exports"

__all__ = ["PROJECT_ROOT", "USER_DATA_DIR", "LOGS_DIR", "EXPORTS_DIR"]
