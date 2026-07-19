import sys
from pathlib import Path

if getattr(sys, "frozen", False):
    BASE_DIR = Path(sys.executable).resolve().parent
else:
    BASE_DIR = Path(__file__).resolve().parent
ASSETS_DIR = BASE_DIR / "assets"
DATA_DIR = BASE_DIR / "data"
EXPORT_DIR = BASE_DIR / "exports"
DB_PATH = DATA_DIR / "pib.db"
LOGO_PATH = ASSETS_DIR / "logo.png"
LOGO_ICO_PATH = ASSETS_DIR / "logo.ico"

NILAI_MAKS = 90
DEFAULT_TOP_N = 5
APP_VERSION = "1.0.0"
APP_TITLE = "Penilaian Praktik Ibadah"

WARNA_HIJAU = "#C6EFCE"
WARNA_KUNING = "#FFEB9C"
WARNA_MERAH = "#FFC7CE"
