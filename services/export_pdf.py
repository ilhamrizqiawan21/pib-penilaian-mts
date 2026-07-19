from __future__ import annotations

from pathlib import Path
from typing import Any

from fpdf import FPDF

from config import LOGO_PATH


def _fmt(value: float | None) -> str:
    return "-" if value is None else f"{value:.1f}"


def _draw_detail_table(pdf: FPDF, detail_grid: dict) -> None:
    headers = detail_grid["headers"]
    rows = detail_grid["rows"]
    page_width = pdf.w - pdf.l_margin - pdf.r_margin
    static_widths = [18, 12, 44]
    final_width = 24
    remaining = max(12, page_width - sum(static_widths) - final_width)
    dynamic_count = max(1, len(headers) - 4)
    dynamic_width = remaining / dynamic_count
    widths = [*static_widths, *([dynamic_width] * dynamic_count), final_width]

    pdf.set_font("Helvetica", "B", 7)
    pdf.set_fill_color(238, 244, 255)
    for header, width in zip(headers, widths):
        pdf.cell(width, 7, str(header)[:18], border=1, fill=True)
    pdf.ln()

    pdf.set_font("Helvetica", "", 7)
    for row in rows:
        values = [row["kelas"], row["no"], row["nama"][:24]]
        for score in row["materi"]:
            values.extend([_fmt(score["hafalan"]), _fmt(score["praktik"])])
        values.append(_fmt(row["rata_akhir"]))
        for value, width in zip(values, widths):
            pdf.cell(width, 6, str(value)[:18], border=1)
        pdf.ln()


def export_laporan_pdf(
    path: str | Path,
    metadata: dict[str, Any],
    rekap_list,
    statistik: dict,
    top_list,
    bottom_list,
    detail_grid: dict | None = None,
) -> str:
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)

    pdf = FPDF(orientation="L", unit="mm", format="A4")
    pdf.set_auto_page_break(auto=True, margin=12)
    pdf.add_page()

    if LOGO_PATH.exists():
        try:
            pdf.image(str(LOGO_PATH), x=12, y=10, w=16, h=16)
        except Exception:
            pass

    pdf.set_font("Helvetica", "B", 14)
    pdf.cell(0, 8, metadata.get("nama_sekolah", ""), ln=True, align="C")
    pdf.set_font("Helvetica", "B", 12)
    pdf.cell(0, 7, "LAPORAN PENILAIAN PRAKTIK IBADAH (PIB)", ln=True, align="C")
    pdf.set_font("Helvetica", "", 10)
    pdf.cell(
        0,
        6,
        f"Tahun Ajaran: {metadata.get('tahun_ajaran', '-')} | Semester: {metadata.get('semester', '-')} | Kelas: {metadata.get('kelas', '-')}",
        ln=True,
        align="C",
    )
    pdf.ln(6)

    pdf.set_font("Helvetica", "B", 11)
    pdf.cell(0, 7, "DETAIL NILAI PER MATERI", ln=True)
    if detail_grid:
        _draw_detail_table(pdf, detail_grid)
    else:
        pdf.cell(0, 7, "Belum ada detail nilai.", ln=True)

    pdf.add_page()
    pdf.set_font("Helvetica", "B", 11)
    pdf.cell(0, 7, "REKAPITULASI NILAI", ln=True)
    headers = ["Rank", "NIS", "Nama", "Kelas", "Hafalan", "Praktik", "Total", "Status"]
    widths = [16, 28, 58, 22, 24, 24, 22, 28]
    pdf.set_fill_color(238, 244, 255)
    for header, width in zip(headers, widths):
        pdf.cell(width, 8, header, border=1, fill=True)
    pdf.ln()
    pdf.set_font("Helvetica", "", 9)
    for item in rekap_list[:18]:
        values = [
            str(item.peringkat or "-"),
            item.nis,
            item.nama[:30],
            item.kelas,
            _fmt(item.rata_hafalan),
            _fmt(item.rata_praktik),
            _fmt(item.rata_total),
            item.status,
        ]
        for value, width in zip(values, widths):
            pdf.cell(width, 7, str(value), border=1)
        pdf.ln()

    pdf.ln(5)
    pdf.set_font("Helvetica", "B", 11)
    pdf.cell(0, 7, "STATISTIK KELAS", ln=True)
    pdf.set_font("Helvetica", "", 10)
    pdf.cell(0, 6, f"Jumlah Siswa: {statistik.get('jumlah_siswa', '-')} | Jumlah Materi: {statistik.get('jumlah_materi', '-')}", ln=True)
    pdf.cell(
        0,
        6,
        f"Rata-rata Kelas: {_fmt(statistik.get('rata_kelas'))} | Lengkap: {statistik.get('jumlah_lengkap', 0)} | Sebagian: {statistik.get('jumlah_sebagian', 0)} | Belum: {statistik.get('jumlah_belum', 0)}",
        ln=True,
    )

    pdf.output(path)
    return str(path)
