# Spesifikasi Lengkap: Aplikasi Penilaian PIB MTs

> **Dokumen ini** adalah blueprint implementasi untuk dibangun via Codex/AI agent.
> Ikuti urutan fase di bagian akhir. Jangan skip unit test — akurasi perhitungan nilai adalah prioritas utama.

---

## 1. Ringkasan Proyek

| Item | Detail |
|------|--------|
| **Nama** | Aplikasi Penilaian Praktik Ibadah (PIB) MTs |
| **Tujuan** | Aplikasi desktop pribadi untuk guru MTs menilai siswa pada aspek **Hafalan** dan **Praktik** |
| **Platform** | Windows Desktop (Python) |
| **Lokasi proyek** | `C:\Users\ilham\pib-penilaian-mts` |
| **Pengguna** | 1 guru (single-user, offline, data lokal) |

### Fitur Wajib

1. Input materi penilaian secara dinamis (bisa berubah sesuai kurikulum)
2. Input jumlah kesalahan per siswa per materi
3. Perhitungan otomatis: skor maks **90** per materi, dikurangi per kesalahan
4. Poin pengurangan **bisa berbeda per materi** (hafalan vs praktik bisa beda)
5. Rata-rata nilai per aspek (hafalan, praktik) dan rata-rata total
6. Peringkat siswa terbaik dan terendah
7. Export laporan **PDF** dan **Excel**
8. Organisasi data per **tahun ajaran**, **semester**, dan **kelas**

---

## 2. Stack Teknologi

```
Python          3.11+
CustomTkinter   >=5.2.0    # UI modern desktop
tksheet         >=7.0.0    # Grid input penilaian (spreadsheet-like)
sqlite3         (stdlib)   # Database lokal
pydantic        >=2.0.0    # Validasi data
openpyxl        >=3.1.0    # Export Excel
fpdf2           >=2.7.0    # Export PDF
```

**Alasan pemilihan:**
- Python: user sudah familiar (proyek referensi: `ppdb-mts-latihan`)
- SQLite: tidak perlu server, aman offline, mudah backup (copy file)
- CustomTkinter + tksheet: UI desktop tanpa Electron, grid penilaian natural
- Pydantic: minimalkan error input invalid

### requirements.txt

```txt
customtkinter>=5.2.0
tksheet>=7.0.0
openpyxl>=3.1.0
fpdf2>=2.7.0
pydantic>=2.0.0
```

---

## 3. Aturan Bisnis (WAJIB DIPATUHI)

### 3.1 Formula Penilaian

```
nilai_materi = max(0, 90 - (jumlah_kesalahan × poin_pengurangan_materi))
```

**Contoh:**
| Materi | Aspek | Poin/kesalahan | Kesalahan | Nilai |
|--------|-------|----------------|-----------|-------|
| Doa makan | hafalan | 2 | 3 | 90 - (3×2) = **84** |
| Sholat berjamaah | praktik | 3 | 5 | 90 - (5×3) = **75** |
| Al-Fatihah | hafalan | 1 | 100 | max(0, ...) = **0** |

### 3.2 Rata-rata Aspek

```
rata_hafalan  = mean(nilai semua materi aspek 'hafalan' yang sudah dinilai)
rata_praktik  = mean(nilai semua materi aspek 'praktik' yang sudah dinilai)
```

- Materi yang **belum dinilai** (belum ada record penilaian) **TIDAK** dihitung dalam rata-rata (bukan dianggap 0).
- Jika semua materi hafalan belum dinilai → `rata_hafalan = null` (tampilkan "-").

### 3.3 Rata-rata Total

```
Jika rata_hafalan DAN rata_praktik ada:
    rata_total = (rata_hafalan + rata_praktik) / 2

Jika hanya satu aspek ada:
    rata_total = nilai aspek yang ada

Jika keduanya null:
    rata_total = null
```

### 3.4 Ranking

- Urutkan descending berdasarkan `rata_total`
- **Tie-break** (nilai sama): `rata_hafalan` desc → `rata_praktik` desc → `nama` asc
- Siswa tanpa `rata_total` (belum ada penilaian sama sekali) **tidak masuk ranking**
- Tampilkan **Top N** (default 5) dan **Bottom N** (default 5), N bisa diatur di UI

### 3.5 Status Kelengkapan Penilaian

```
status = "lengkap"  jika semua materi aktif semester ini sudah dinilai
status = "sebagian"   jika sebagian materi sudah dinilai
status = "belum"      jika belum ada penilaian
```

---

## 4. Struktur Folder Proyek

```
pib-penilaian-mts/
├── main.py
├── config.py
├── requirements.txt
├── README.md
├── SPEC.md                  # file ini
├── data/
│   └── pib.db               # auto-created saat first run
├── exports/                 # auto-created, output PDF/Excel
├── database/
│   ├── __init__.py
│   ├── connection.py        # koneksi + init schema
│   ├── schema.sql           # DDL referensi
│   └── repository.py        # semua query CRUD
├── models/
│   ├── __init__.py
│   ├── periode.py           # TahunAjaran, Semester, Kelas
│   ├── siswa.py
│   ├── materi.py
│   └── penilaian.py
├── services/
│   ├── __init__.py
│   ├── penilaian_service.py # logika hitung nilai, rata-rata, ranking
│   ├── export_excel.py
│   └── export_pdf.py
├── ui/
│   ├── __init__.py
│   ├── app.py               # main window + sidebar
│   ├── wizard.py            # first-run setup
│   ├── dashboard_view.py
│   ├── periode_view.py      # kelola TA, semester, kelas
│   ├── siswa_view.py
│   ├── materi_view.py
│   ├── penilaian_view.py    # grid tksheet
│   ├── laporan_view.py
│   └── components/
│       ├── __init__.py
│       ├── dialogs.py       # form popup reusable
│       └── table_helpers.py
└── tests/
    ├── __init__.py
    └── test_penilaian.py
```

---

## 5. Database Schema

### 5.1 DDL Lengkap (`database/schema.sql`)

```sql
PRAGMA foreign_keys = ON;

CREATE TABLE IF NOT EXISTS pengaturan (
    key   TEXT PRIMARY KEY,
    value TEXT NOT NULL
);
-- key: 'nama_sekolah', value: 'MTs Al-Hikmah'

CREATE TABLE IF NOT EXISTS tahun_ajaran (
    id        INTEGER PRIMARY KEY AUTOINCREMENT,
    nama      TEXT NOT NULL UNIQUE,       -- '2026/2027'
    is_aktif  INTEGER NOT NULL DEFAULT 0  -- hanya 1 aktif
);

CREATE TABLE IF NOT EXISTS semester (
    id              INTEGER PRIMARY KEY AUTOINCREMENT,
    tahun_ajaran_id INTEGER NOT NULL REFERENCES tahun_ajaran(id) ON DELETE CASCADE,
    nama            TEXT NOT NULL,        -- 'Ganjil' | 'Genap'
    is_aktif        INTEGER NOT NULL DEFAULT 0,
    UNIQUE(tahun_ajaran_id, nama)
);

CREATE TABLE IF NOT EXISTS kelas (
    id      INTEGER PRIMARY KEY AUTOINCREMENT,
    nama    TEXT NOT NULL UNIQUE,   -- '7A', '8B'
    tingkat INTEGER NOT NULL        -- 7, 8, 9
);

CREATE TABLE IF NOT EXISTS siswa (
    id          INTEGER PRIMARY KEY AUTOINCREMENT,
    nis         TEXT NOT NULL,
    nama        TEXT NOT NULL,
    kelas_id    INTEGER NOT NULL REFERENCES kelas(id),
    semester_id INTEGER NOT NULL REFERENCES semester(id) ON DELETE CASCADE,
    is_aktif    INTEGER NOT NULL DEFAULT 1,
    UNIQUE(nis, semester_id)
);

CREATE TABLE IF NOT EXISTS materi (
    id               INTEGER PRIMARY KEY AUTOINCREMENT,
    semester_id      INTEGER NOT NULL REFERENCES semester(id) ON DELETE CASCADE,
    nama             TEXT NOT NULL,
    aspek            TEXT NOT NULL CHECK(aspek IN ('hafalan', 'praktik')),
    poin_pengurangan REAL NOT NULL CHECK(poin_pengurangan > 0),
    urutan           INTEGER NOT NULL DEFAULT 0,
    is_aktif         INTEGER NOT NULL DEFAULT 1,
    UNIQUE(semester_id, nama)
);

CREATE TABLE IF NOT EXISTS penilaian (
    id               INTEGER PRIMARY KEY AUTOINCREMENT,
    siswa_id         INTEGER NOT NULL REFERENCES siswa(id) ON DELETE CASCADE,
    materi_id        INTEGER NOT NULL REFERENCES materi(id) ON DELETE CASCADE,
    jumlah_kesalahan INTEGER NOT NULL CHECK(jumlah_kesalahan >= 0),
    nilai            REAL NOT NULL CHECK(nilai >= 0 AND nilai <= 90),
    poin_snapshot    REAL NOT NULL,   -- snapshot poin_pengurangan saat save
    updated_at       TEXT NOT NULL,   -- ISO 8601
    UNIQUE(siswa_id, materi_id)
);

CREATE INDEX IF NOT EXISTS idx_siswa_semester_kelas
    ON siswa(semester_id, kelas_id);
CREATE INDEX IF NOT EXISTS idx_materi_semester
    ON materi(semester_id, is_aktif);
CREATE INDEX IF NOT EXISTS idx_penilaian_siswa
    ON penilaian(siswa_id);
CREATE INDEX IF NOT EXISTS idx_penilaian_materi
    ON penilaian(materi_id);
```

### 5.2 Catatan Schema

- `poin_snapshot` disimpan agar jika materi diubah nanti, nilai historis tetap bisa diaudit.
- Saat materi `poin_pengurangan` diubah, tampilkan dialog: *"Recalculate semua penilaian materi ini?"* — jika ya, update semua record penilaian terkait.
- Soft delete: gunakan `is_aktif = 0`, jangan hard delete jika sudah ada penilaian.

---

## 6. Models (Pydantic)

### 6.1 `models/periode.py`

```python
from pydantic import BaseModel, field_validator

class TahunAjaranCreate(BaseModel):
    nama: str  # "2026/2027"

    @field_validator("nama")
    @classmethod
    def valid_format(cls, v: str) -> str:
        v = v.strip()
        if "/" not in v:
            raise ValueError("Format tahun ajaran: YYYY/YYYY")
        return v

class SemesterCreate(BaseModel):
    tahun_ajaran_id: int
    nama: str  # "Ganjil" | "Genap"

    @field_validator("nama")
    @classmethod
    def valid_nama(cls, v: str) -> str:
        v = v.strip().capitalize()
        if v not in ("Ganjil", "Genap"):
            raise ValueError("Semester harus Ganjil atau Genap")
        return v

class KelasCreate(BaseModel):
    nama: str       # "7A"
    tingkat: int    # 7, 8, 9

    @field_validator("tingkat")
    @classmethod
    def valid_tingkat(cls, v: int) -> int:
        if v not in (7, 8, 9):
            raise ValueError("Tingkat harus 7, 8, atau 9")
        return v
```

### 6.2 `models/siswa.py`

```python
from pydantic import BaseModel, field_validator

class SiswaCreate(BaseModel):
    nis: str
    nama: str
    kelas_id: int
    semester_id: int

    @field_validator("nis", "nama")
    @classmethod
    def not_empty(cls, v: str) -> str:
        v = v.strip()
        if not v:
            raise ValueError("Tidak boleh kosong")
        return v
```

### 6.3 `models/materi.py`

```python
from pydantic import BaseModel, field_validator
from typing import Literal

class MateriCreate(BaseModel):
    semester_id: int
    nama: str
    aspek: Literal["hafalan", "praktik"]
    poin_pengurangan: float
    urutan: int = 0

    @field_validator("poin_pengurangan")
    @classmethod
    def positive(cls, v: float) -> float:
        if v <= 0:
            raise ValueError("Poin pengurangan harus > 0")
        return v
```

### 6.4 `models/penilaian.py`

```python
from pydantic import BaseModel, field_validator

class PenilaianInput(BaseModel):
    siswa_id: int
    materi_id: int
    jumlah_kesalahan: int

    @field_validator("jumlah_kesalahan")
    @classmethod
    def non_negative(cls, v: int) -> int:
        if v < 0:
            raise ValueError("Jumlah kesalahan tidak boleh negatif")
        return v
```

---

## 7. Services — Logika Inti

### 7.1 `services/penilaian_service.py`

Implementasi **PERSIS** seperti berikut:

```python
from __future__ import annotations
from dataclasses import dataclass
from typing import Literal

NILAI_MAKS = 90

def hitung_nilai(jumlah_kesalahan: int, poin_pengurangan: float) -> float:
    """Hitung nilai materi. Floor di 0."""
    return max(0.0, NILAI_MAKS - jumlah_kesalahan * poin_pengurangan)


def rata_rata(values: list[float]) -> float | None:
    if not values:
        return None
    return sum(values) / len(values)


@dataclass
class RekapSiswa:
    siswa_id: int
    nis: str
    nama: str
    kelas: str
    rata_hafalan: float | None
    rata_praktik: float | None
    rata_total: float | None
    status: Literal["lengkap", "sebagian", "belum"]
    peringkat: int | None = None


def hitung_rata_total(rata_hafalan: float | None, rata_praktik: float | None) -> float | None:
    if rata_hafalan is not None and rata_praktik is not None:
        return (rata_hafalan + rata_praktik) / 2
    if rata_hafalan is not None:
        return rata_hafalan
    if rata_praktik is not None:
        return rata_praktik
    return None


def tentukan_status(jumlah_dinilai: int, jumlah_materi_aktif: int) -> str:
    if jumlah_materi_aktif == 0 or jumlah_dinilai == 0:
        return "belum"
    if jumlah_dinilai >= jumlah_materi_aktif:
        return "lengkap"
    return "sebagian"


def hitung_ranking(rekap_list: list[RekapSiswa]) -> list[RekapSiswa]:
    """Sort dan assign peringkat. Siswa tanpa rata_total di akhir tanpa peringkat."""
    with_score = [r for r in rekap_list if r.rata_total is not None]
    without_score = [r for r in rekap_list if r.rata_total is None]

    with_score.sort(
        key=lambda r: (
            -r.rata_total,
            -(r.rata_hafalan or 0),
            -(r.rata_praktik or 0),
            r.nama.lower(),
        )
    )

    for i, r in enumerate(with_score, start=1):
        r.peringkat = i
    for r in without_score:
        r.peringkat = None

    return with_score + without_score


def ambil_top_bottom(ranked: list[RekapSiswa], n: int = 5) -> tuple[list[RekapSiswa], list[RekapSiswa]]:
    scored = [r for r in ranked if r.peringkat is not None]
    top = scored[:n]
    bottom = list(reversed(scored[-n:])) if len(scored) >= n else list(reversed(scored))
    return top, bottom
```

### 7.2 Fungsi Repository yang Dibutuhkan (`database/repository.py`)

Implementasikan class `Repository` dengan method:

```python
class Repository:
    # --- Pengaturan ---
    def get_pengaturan(self, key: str) -> str | None
    def set_pengaturan(self, key: str, value: str) -> None

    # --- Tahun Ajaran ---
    def list_tahun_ajaran(self) -> list[dict]
    def create_tahun_ajaran(self, nama: str) -> int
    def set_tahun_ajaran_aktif(self, id: int) -> None
    def get_tahun_ajaran_aktif(self) -> dict | None

    # --- Semester ---
    def list_semester(self, tahun_ajaran_id: int) -> list[dict]
    def create_semester(self, tahun_ajaran_id: int, nama: str) -> int
    def set_semester_aktif(self, id: int) -> None
    def get_semester_aktif(self) -> dict | None

    # --- Kelas ---
    def list_kelas(self) -> list[dict]
    def create_kelas(self, nama: str, tingkat: int) -> int
    def update_kelas(self, id: int, nama: str, tingkat: int) -> None
    def delete_kelas(self, id: int) -> None  # raise jika masih ada siswa

    # --- Siswa ---
    def list_siswa(self, semester_id: int, kelas_id: int | None = None) -> list[dict]
    def create_siswa(self, data: dict) -> int
    def update_siswa(self, id: int, data: dict) -> None
    def deactivate_siswa(self, id: int) -> None

    # --- Materi ---
    def list_materi(self, semester_id: int, hanya_aktif: bool = True) -> list[dict]
    def create_materi(self, data: dict) -> int
    def update_materi(self, id: int, data: dict) -> None
    def deactivate_materi(self, id: int) -> None
    def salin_materi_ke_semester(self, dari_semester_id: int, ke_semester_id: int) -> int
    # return jumlah materi disalin

    # --- Penilaian ---
    def get_penilaian_grid(self, semester_id: int, kelas_id: int) -> dict
    # return: {siswa_list, materi_list, penilaian_map: {(siswa_id, materi_id): {jumlah_kesalahan, nilai}}}

    def upsert_penilaian_batch(self, records: list[dict]) -> None
    # setiap record: {siswa_id, materi_id, jumlah_kesalahan, nilai, poin_snapshot, updated_at}

    def recalculate_penilaian_by_materi(self, materi_id: int, poin_baru: float) -> int
    # return jumlah record diupdate

    # --- Rekap ---
    def get_rekap_kelas(self, semester_id: int, kelas_id: int) -> list[RekapSiswa]
    def get_rekap_semester(self, semester_id: int) -> list[RekapSiswa]
    def get_statistik_kelas(self, semester_id: int, kelas_id: int) -> dict
    # return: {jumlah_siswa, jumlah_materi, rata_kelas, jumlah_lengkap, jumlah_sebagian, jumlah_belum}
```

---

## 8. Export

### 8.1 Excel (`services/export_excel.py`)

**Fungsi:** `export_laporan_excel(path, metadata, rekap_list, detail_grid) -> str`

**metadata:**
```python
{
    "nama_sekolah": "MTs Al-Hikmah",
    "tahun_ajaran": "2026/2027",
    "semester": "Ganjil",
    "kelas": "7A",
    "tanggal_export": "2026-07-18",
}
```

**Sheet "Rekap":**
| Peringkat | NIS | Nama | Kelas | Rata Hafalan | Rata Praktik | Rata Total | Status |
|-----------|-----|------|-------|--------------|--------------|------------|--------|

**Sheet "Detail Materi":**
- Baris 1-3: header metadata
- Baris 5: header kolom → No, NIS, Nama, [materi1], [materi2], ...
- Group header materi: kolom hafalan diberi prefix `[H]`, praktik `[P]`
- Isi sel: nilai (bukan jumlah kesalahan)
- Kolom kosong jika belum dinilai

**Styling:**
- Header bold, background abu-abu terang
- Freeze row header
- Auto-width kolom

### 8.2 PDF (`services/export_pdf.py`)

**Fungsi:** `export_laporan_pdf(path, metadata, rekap_list, statistik, top_list, bottom_list) -> str`

**Layout:**
```
[NAMA SEKOLAH]
LAPORAN PENILAIAN PRAKTIK IBADAH (PIB)
Tahun Ajaran: ... | Semester: ... | Kelas: ...
Tanggal: ...

--- REKAPITULASI NILAI ---
[tabel: Peringkat | NIS | Nama | Rata Hafalan | Rata Praktik | Rata Total]

--- STATISTIK KELAS ---
Jumlah Siswa    : ...
Jumlah Materi   : ...
Rata-rata Kelas : ...
Lengkap         : ... siswa
Sebagian        : ... siswa
Belum Dinilai   : ... siswa

--- PERINGKAT TERBAIK (Top 5) ---
[tabel ringkas]

--- PERLU PERHATIAN (Bottom 5) ---
[tabel ringkas]
```

Gunakan `fpdf2` dengan font Helvetica. Landscape jika kolom > 6.

**Naming file:**
```
exports/PIB_{kelas}_{tahun_ajaran}-{semester}_{YYYY-MM-DD}.xlsx
exports/PIB_{kelas}_{tahun_ajaran}-{semester}_{YYYY-MM-DD}.pdf
```

---

## 9. UI Specification

### 9.1 Window Utama (`ui/app.py`)

```
┌─────────────────────────────────────────────────────────────┐
│  MTs Al-Hikmah  |  2026/2027 Ganjil  |  Kelas: [7A ▼]      │  ← header bar
├──────────┬──────────────────────────────────────────────────┤
│ Dashboard│                                                  │
│ Periode  │              [Content Area]                      │
│ Siswa    │                                                  │
│ Materi   │                                                  │
│ Penilaian│                                                  │
│ Laporan  │                                                  │
│          │                                                  │
│ v1.0.0   │                                                  │
└──────────┴──────────────────────────────────────────────────┘
```

- Window size: 1200×750, min 900×600
- Theme: CustomTkinter `blue` / mode `light`
- Sidebar width: 200px
- Content area: frame yang di-swap saat navigasi

### 9.2 First-Run Wizard (`ui/wizard.py`)

Tampilkan jika DB kosong (tidak ada tahun ajaran):

**Step 1:** Nama sekolah
**Step 2:** Tahun ajaran (default: tahun sekarang)
**Step 3:** Semester (Ganjil/Genap)
**Step 4:** Tambah kelas (minimal 1, bisa tambah banyak: 7A, 7B, ...)
**Step 5:** Selesai → masuk main window

### 9.3 Dashboard (`ui/dashboard_view.py`)

Kartu statistik (4 cards):
- Total Siswa (semester aktif)
- Total Materi Aktif
- Rata-rata Kelas (jika ada penilaian)
- Siswa Belum Lengkap

Tabel ringkas: 5 siswa terbaik (nama + rata total)

### 9.4 Periode View (`ui/periode_view.py`)

Tab/section:
1. **Tahun Ajaran** — list, tambah, set aktif
2. **Semester** — list per TA, tambah, set aktif
3. **Kelas** — CRUD kelas

### 9.5 Siswa View (`ui/siswa_view.py`)

- Dropdown filter kelas
- Tabel: NIS | Nama | Kelas | Status | Aksi (Edit, Nonaktifkan)
- Tombol "Tambah Siswa" → dialog form
- Validasi: NIS unik per semester

### 9.6 Materi View (`ui/materi_view.py`)

- Tabel grouped: section Hafalan, section Praktik
- Kolom: Urutan | Nama | Aspek | Poin/Kesalahan | Status | Aksi
- Tombol: Tambah Materi, Salin dari Semester Lain
- Dialog salin: pilih semester sumber → konfirmasi

### 9.7 Penilaian View (`ui/penilaian_view.py`) — PALING PENTING

**Layout:**
```
Kelas: [7A ▼]    [Simpan Penilaian]    [Refresh]

┌─────┬──────┬──────────┬─────────┬─────────┬─────────┐
│ No  │ NIS  │ Nama     │[H] Doa  │[H] Fatih│[P] Sholat│ ...
├─────┼──────┼──────────┼─────────┼─────────┼─────────┤
│ 1   │ 001  │ Ahmad    │ 2       │ 0       │ 1       │
│ 2   │ 002  │ Budi     │         │ 3       │         │
└─────┴──────┴──────────┴─────────┴─────────┴─────────┘

Preview nilai (read-only baris bawah atau tooltip):
Ahmad → Doa: 86 | Fatih: 90 | Sholat: 87
```

**Implementasi tksheet:**
- Kolom 0-2: No, NIS, Nama → **readonly**
- Kolom 3+: input jumlah kesalahan (integer only)
- Validasi on save: tolak nilai negatif atau non-integer
- Saat cell edit selesai: update preview nilai di status bar
- Warna baris berdasarkan rata sementara (opsional fase polish)

**Flow save:**
1. Kumpulkan semua sel yang terisi
2. Validasi via `PenilaianInput`
3. Hitung nilai via `hitung_nilai()`
4. `upsert_penilaian_batch()`
5. Toast/snackbar "Penilaian berhasil disimpan"

### 9.8 Laporan View (`ui/laporan_view.py`)

**Filter:** Kelas (dropdown + opsi "Semua Kelas")

**Section 1 — Tabel Rekap Lengkap**
Semua siswa dengan peringkat, rata hafalan, rata praktik, rata total, status

**Section 2 — Top 5 / Bottom 5**
Dua tabel side-by-side

**Section 3 — Export**
- Tombol "Export Excel" → filedialog save (default ke exports/)
- Tombol "Export PDF" → filedialog save
- Input "Jumlah ranking" (default 5)

---

## 10. Config (`config.py`)

```python
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent
DATA_DIR = BASE_DIR / "data"
EXPORT_DIR = BASE_DIR / "exports"
DB_PATH = DATA_DIR / "pib.db"

NILAI_MAKS = 90
DEFAULT_TOP_N = 5
APP_VERSION = "1.0.0"
APP_TITLE = "Penilaian PIB MTs"

# Warna preview nilai (hex for tksheet/tags)
WARNA_HIJAU = "#C6EFCE"   # >= 80
WARNA_KUNING = "#FFEB9C"  # 60-79
WARNA_MERAH  = "#FFC7CE"  # < 60
```

Pastikan `DATA_DIR` dan `EXPORT_DIR` dibuat otomatis saat startup.

---

## 11. Entry Point (`main.py`)

```python
#!/usr/bin/env python3
"""Aplikasi Penilaian PIB MTs — Entry Point"""

import sys
from pathlib import Path

# Pastikan root project ada di sys.path
sys.path.insert(0, str(Path(__file__).resolve().parent))

from config import DATA_DIR, EXPORT_DIR
from database.connection import init_db
from ui.app import PIBApp


def main():
    DATA_DIR.mkdir(parents=True, exist_ok=True)
    EXPORT_DIR.mkdir(parents=True, exist_ok=True)
    init_db()
    app = PIBApp()
    app.mainloop()


if __name__ == "__main__":
    main()
```

---

## 12. Unit Tests (`tests/test_penilaian.py`)

**WAJIB lulus semua sebelum UI dianggap selesai.**

```python
import pytest
from services.penilaian_service import (
    hitung_nilai, rata_rata, hitung_rata_total,
    tentukan_status, hitung_ranking, ambil_top_bottom, RekapSiswa, NILAI_MAKS
)

class TestHitungNilai:
    def test_sempurna(self):
        assert hitung_nilai(0, 2) == 90

    def test_dengan_kesalahan(self):
        assert hitung_nilai(3, 2) == 84

    def test_floor_nol(self):
        assert hitung_nilai(100, 1) == 0

    def test_poin_desimal(self):
        assert hitung_nilai(2, 2.5) == 85.0


class TestRataRata:
    def test_normal(self):
        assert rata_rata([80, 90, 70]) == 80.0

    def test_kosong(self):
        assert rata_rata([]) is None


class TestRataTotal:
    def test_kedua_aspek(self):
        assert hitung_rata_total(80, 90) == 85.0

    def test_hanya_hafalan(self):
        assert hitung_rata_total(80, None) == 80.0

    def test_keduanya_null(self):
        assert hitung_rata_total(None, None) is None


class TestStatus:
    def test_belum(self):
        assert tentukan_status(0, 5) == "belum"

    def test_sebagian(self):
        assert tentukan_status(2, 5) == "sebagian"

    def test_lengkap(self):
        assert tentukan_status(5, 5) == "lengkap"


class TestRanking:
    def _make(self, nama, total, hafalan=None, praktik=None):
        return RekapSiswa(
            siswa_id=1, nis="001", nama=nama, kelas="7A",
            rata_hafalan=hafalan, rata_praktik=praktik,
            rata_total=total, status="lengkap"
        )

    def test_urutan_desc(self):
        data = [self._make("Budi", 70), self._make("Ahmad", 90)]
        ranked = hitung_ranking(data)
        assert ranked[0].nama == "Ahmad"
        assert ranked[0].peringkat == 1

    def test_tie_break_nama(self):
        data = [self._make("Budi", 85, 80, 90), self._make("Ahmad", 85, 80, 90)]
        ranked = hitung_ranking(data)
        assert ranked[0].nama == "Ahmad"  # ascending nama

    def test_tanpa_nilai_no_rank(self):
        data = [self._make("Ahmad", None)]
        ranked = hitung_ranking(data)
        assert ranked[0].peringkat is None


class TestTopBottom:
    def test_top_5(self):
        ranked = [
            RekapSiswa(i, f"00{i}", f"S{i}", "7A", 90-i, 90-i, 90-i, "lengkap", i)
            for i in range(1, 11)
        ]
        top, bottom = ambil_top_bottom(ranked, 5)
        assert len(top) == 5
        assert top[0].peringkat == 1
```

Jalankan: `python -m pytest tests/ -v`

---

## 13. Data Contoh (Seed / Testing Manual)

### Tahun Ajaran & Semester
```
TA: 2026/2027 (aktif)
Semester: Ganjil (aktif)
```

### Kelas
```
7A (tingkat 7), 7B (tingkat 7), 8A (tingkat 8)
```

### Materi (semester Ganjil)
| Urutan | Nama | Aspek | Poin/Kesalahan |
|--------|------|-------|----------------|
| 1 | Doa sebelum makan | hafalan | 2 |
| 2 | Surat Al-Fatihah | hafalan | 1 |
| 3 | Surat An-Naas | hafalan | 1 |
| 4 | Wudhu | praktik | 3 |
| 5 | Sholat berjamaah | praktik | 3 |

### Siswa (7A)
```
001 - Ahmad Fauzi
002 - Budi Santoso
003 - Citra Dewi
004 - Dedi Pratama
005 - Eka Putri
```

### Contoh Penilaian Ahmad (001)
| Materi | Kesalahan | Nilai |
|--------|-----------|-------|
| Doa sebelum makan | 2 | 86 |
| Al-Fatihah | 0 | 90 |
| An-Naas | 1 | 89 |
| Wudhu | 3 | 81 |
| Sholat berjamaah | 2 | 84 |

```
rata_hafalan = (86 + 90 + 89) / 3 = 88.33
rata_praktik = (81 + 84) / 2 = 82.50
rata_total   = (88.33 + 82.50) / 2 = 85.42
```

---

## 14. Error Handling

| Situasi | Respons UI |
|---------|-----------|
| NIS duplikat | Dialog error: "NIS sudah terdaftar di semester ini" |
| Hapus kelas yang punya siswa | Block + pesan: "Pindahkan/nonaktifkan siswa dulu" |
| Input kesalahan negatif | Highlight sel merah, block save |
| Input bukan angka di grid | Revert ke nilai sebelumnya |
| Export gagal (folder tidak ada) | Auto-create exports/ lalu retry |
| DB corrupt | Tampilkan pesan + instruksi restore backup |
| Ubah poin materi yang sudah dinilai | Dialog konfirmasi recalculate |

---

## 15. README.md (Template)

Buat README dengan isi:
1. Deskripsi singkat aplikasi
2. Requirements: Python 3.11+
3. Instalasi: `pip install -r requirements.txt`
4. Menjalankan: `python main.py`
5. Panduan penggunaan step-by-step (wizard → materi → siswa → penilaian → laporan)
6. Backup: copy file `data/pib.db`
7. Restore: replace `data/pib.db` dengan backup
8. Menjalankan test: `python -m pytest tests/ -v`

---

## 16. Urutan Implementasi untuk Codex

Ikuti fase ini **berurutan**. Setiap fase selesai = harus bisa ditest sebelum lanjut.

### Fase 1 — Foundation
```
[ ] Buat struktur folder + requirements.txt + config.py
[ ] database/connection.py — init_db() baca & execute schema.sql
[ ] database/repository.py — implement semua CRUD (tanpa UI dulu)
[ ] services/penilaian_service.py — copy logic dari section 7.1
[ ] tests/test_penilaian.py — semua test lulus
[ ] Verifikasi: python -m pytest tests/ -v → ALL PASSED
```

### Fase 2 — UI Shell
```
[ ] ui/app.py — main window + sidebar navigasi
[ ] ui/wizard.py — first-run setup
[ ] ui/dashboard_view.py — placeholder cards
[ ] main.py — wire everything
[ ] Verifikasi: python main.py → wizard muncul, DB terbuat
```

### Fase 3 — Master Data
```
[ ] ui/periode_view.py — CRUD TA, semester, kelas
[ ] ui/siswa_view.py — CRUD siswa
[ ] ui/materi_view.py — CRUD materi + salin semester
[ ] Verifikasi: bisa input siswa & materi, data persist setelah restart
```

### Fase 4 — Penilaian Grid
```
[ ] ui/penilaian_view.py — tksheet grid
[ ] Wire save ke repository + penilaian_service
[ ] Preview nilai di status bar
[ ] Verifikasi: input kesalahan → save → restart → data masih ada → nilai benar
```

### Fase 5 — Laporan & Export
```
[ ] ui/laporan_view.py — tabel rekap + top/bottom
[ ] services/export_excel.py
[ ] services/export_pdf.py
[ ] ui/dashboard_view.py — isi statistik real
[ ] Verifikasi: export file terbuka di Excel/PDF reader, angka match DB
```

### Fase 6 — Polish
```
[ ] Error handling semua view
[ ] README.md
[ ] Test end-to-end dengan data contoh section 13
[ ] (Opsional) PyInstaller spec untuk .exe
```

---

## 17. Prompt untuk Codex

Copy-paste prompt ini ke Codex:

---

**Prompt:**

```
Bangun aplikasi desktop Python sesuai spesifikasi di file SPEC.md.

Rules:
1. Ikuti urutan Fase 1→6 di section 16
2. Implementasi formula penilaian PERSIS seperti section 3 dan 7.1 — jangan ubah
3. Semua unit test di section 12 WAJIB lulus sebelum lanjut ke UI
4. Gunakan sqlite3 stdlib (bukan SQLAlchemy) untuk kesederhanaan
5. UI bahasa Indonesia
6. Jangan gunakan dependency di luar requirements.txt
7. Setiap fase, beritahu saya cara verifikasi manual

Mulai dari Fase 1. Buat semua file yang disebutkan di section 4.
```

---

## 18. Checklist Akhir (Definition of Done)

- [ ] `python main.py` berjalan tanpa error di Windows
- [ ] First-run wizard berfungsi
- [ ] CRUD siswa, materi, kelas, semester berfungsi
- [ ] Grid penilaian: input kesalahan → nilai terhitung benar
- [ ] Rata hafalan, rata praktik, rata total benar (verifikasi dengan data contoh section 13)
- [ ] Ranking top/bottom benar
- [ ] Export Excel: 2 sheet, angka match
- [ ] Export PDF: readable, angka match
- [ ] `python -m pytest tests/ -v` → ALL PASSED
- [ ] Data persist setelah restart aplikasi
- [ ] README ada panduan penggunaan

---

*Dokumen spec v1.0 — Aplikasi Penilaian PIB MTs*
*Dibuat untuk implementasi via Codex*
