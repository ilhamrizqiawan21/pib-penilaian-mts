#!/usr/bin/env python3
from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

from config import ASSETS_DIR, DATA_DIR, EXPORT_DIR
from database.connection import init_db
from ui.app import PIBApp


def main() -> None:
    ASSETS_DIR.mkdir(parents=True, exist_ok=True)
    DATA_DIR.mkdir(parents=True, exist_ok=True)
    EXPORT_DIR.mkdir(parents=True, exist_ok=True)
    init_db()
    app = PIBApp()
    app.mainloop()


if __name__ == "__main__":
    main()
