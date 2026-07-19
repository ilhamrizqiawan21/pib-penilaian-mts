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


def ambil_top_bottom(
    ranked: list[RekapSiswa], n: int = 5
) -> tuple[list[RekapSiswa], list[RekapSiswa]]:
    scored = [r for r in ranked if r.peringkat is not None]
    top = scored[:n]
    bottom = list(reversed(scored[-n:])) if len(scored) >= n else list(reversed(scored))
    return top, bottom
