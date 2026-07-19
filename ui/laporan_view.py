from __future__ import annotations

import json
from datetime import date
from tkinter import filedialog, messagebox

import customtkinter as ctk

from config import EXPORT_DIR
from services.export_excel import export_laporan_excel
from services.export_pdf import export_laporan_pdf
from services.penilaian_service import ambil_top_bottom
from ui import theme
from ui.components.widgets import (
    EmptyState,
    SectionCard,
    StatCard,
    TableHeader,
    TableRow,
    badge,
    primary_button,
    secondary_button,
    show_loading,
    show_toast,
    styled_option,
)


class LaporanView(ctk.CTkFrame):
    def __init__(self, master, repo, refresh_callback):
        super().__init__(master, fg_color=theme.BACKGROUND)
        self.repo = repo
        self.refresh_callback = refresh_callback
        self.semester = repo.get_semester_aktif()
        self.kelas_list = repo.list_kelas()
        self.kelas_map = {"Semua Kelas": None, **{k["nama"]: k["id"] for k in self.kelas_list}}
        self.kelas_var = ctk.StringVar(value="Semua Kelas")
        self.grid_columnconfigure(0, weight=1)

        hero = ctk.CTkFrame(self, fg_color=theme.SURFACE_ACCENT, border_color=theme.BORDER, border_width=1, corner_radius=12)
        hero.grid(row=0, column=0, sticky="ew", pady=(0, 18))
        hero.grid_columnconfigure(0, weight=1)
        ctk.CTkLabel(hero, text="Laporan Hasil Penilaian", font=(theme.FONT, 26, "bold"), text_color=theme.TEXT).grid(
            row=0, column=0, sticky="w", padx=20, pady=(18, 4)
        )
        ctk.CTkLabel(
            hero,
            text="Rekap nilai, ranking terbaik/terendah, dan persiapan export laporan.",
            font=(theme.FONT, 14),
            text_color=theme.TEXT_MUTED,
        ).grid(row=1, column=0, sticky="w", padx=20, pady=(0, 18))

        if not self.semester:
            EmptyState(self, "Belum ada semester aktif", "Buat periode aktif sebelum melihat laporan.").grid(row=1, column=0, sticky="ew")
            return

        self._filter().grid(row=1, column=0, sticky="ew", pady=(0, 18))
        self.body = ctk.CTkFrame(self, fg_color=theme.BACKGROUND)
        self.body.grid(row=2, column=0, sticky="ew")
        self.body.grid_columnconfigure(0, weight=1)
        self.load()

    def _filter(self):
        bar = ctk.CTkFrame(self, fg_color=theme.SURFACE, border_color=theme.BORDER, border_width=1, corner_radius=theme.RADIUS)
        ctk.CTkLabel(bar, text="Pilih Kelas", font=(theme.FONT, 13, "bold"), text_color=theme.TEXT_MUTED).pack(side="left", padx=(16, 8), pady=14)
        styled_option(bar, list(self.kelas_map), self.kelas_var, command=lambda _: self.load(), width=170).pack(side="left", pady=14)
        secondary_button(bar, "Export Excel", command=self.export_excel).pack(side="right", padx=(8, 16), pady=14)
        primary_button(bar, "Cetak PDF", command=self.export_pdf).pack(side="right", padx=8, pady=14)
        secondary_button(bar, "Import JSON", command=self.import_json_backup).pack(side="right", padx=8, pady=14)
        secondary_button(bar, "Backup JSON", command=self.export_json_backup).pack(side="right", padx=8, pady=14)
        return bar

    def load(self):
        for child in self.body.winfo_children():
            child.destroy()
        kelas_id = self.kelas_map.get(self.kelas_var.get())
        if kelas_id is None:
            rekap = self.repo.get_rekap_semester(self.semester["id"])
            stats_cards = [
                ("Total Siswa", str(len(rekap)), "#84E9DD", "S"),
                ("Sudah Dinilai", str(sum(1 for r in rekap if r.rata_total is not None)), "#D0E1FB", "N"),
            ]
        else:
            rekap = self.repo.get_rekap_kelas(self.semester["id"], kelas_id)
            stats = self.repo.get_statistik_kelas(self.semester["id"], kelas_id)
            stats_cards = [
                ("Total Siswa", str(stats["jumlah_siswa"]), "#84E9DD", "S"),
                ("Rata Kelas", "-" if stats["rata_kelas"] is None else f"{stats['rata_kelas']:.1f}", "#D0E1FB", "N"),
            ]

        top, bottom = ambil_top_bottom(rekap, 5)
        cards = ctk.CTkFrame(self.body, fg_color=theme.BACKGROUND)
        cards.grid(row=0, column=0, sticky="ew", pady=(0, 18))
        cards.grid_columnconfigure((0, 1), weight=1)
        for i, (title, value, accent, icon) in enumerate(stats_cards):
            StatCard(cards, title, value, accent, icon=icon).grid(row=0, column=i, sticky="ew", padx=(0 if i == 0 else 10, 0))

        detail = self.repo.get_laporan_detail(self.semester["id"], kelas_id)
        self._detail_table(detail).grid(row=1, column=0, sticky="ew")
        self._ranking_table("Peringkat Siswa", rekap).grid(row=2, column=0, sticky="ew", pady=(18, 0))
        rank_row = ctk.CTkFrame(self.body, fg_color=theme.BACKGROUND)
        rank_row.grid(row=3, column=0, sticky="ew", pady=(18, 0))
        rank_row.grid_columnconfigure((0, 1), weight=1)
        self._mini_table("Terbaik", top).grid(row=0, column=0, sticky="ew", padx=(0, 10))
        self._mini_table("Perlu Perhatian", bottom).grid(row=0, column=1, sticky="ew", padx=(10, 0))

    def _detail_table(self, detail: dict):
        card = SectionCard(
            self.body,
            "Detail Nilai Per Materi",
            "Format export: Kelas, No, Nama, nilai Hafalan dan Praktik per materi, serta rata-rata akhir.",
        )
        header_columns = [("Kelas", 70), ("No", 48), ("Nama", 220)]
        for name in detail["materi_names"]:
            header_columns.extend([(f"{name} H", 86), (f"{name} P", 86)])
        header_columns.append(("Rata Akhir", 100))
        TableHeader(card.body, header_columns).pack(fill="x", padx=0)
        preview_rows = detail["rows"][:12]
        if not preview_rows:
            EmptyState(card.body, "Belum ada data laporan", "Tambahkan siswa, materi, dan penilaian terlebih dahulu.").pack(fill="x", padx=14, pady=14)
            return card
        for idx, row in enumerate(preview_rows, start=1):
            item = TableRow(card.body, idx)
            item.pack(fill="x", pady=2)
            values = [row["kelas"], str(row["no"]), row["nama"]]
            widths = [70, 48, 220]
            for score in row["materi"]:
                values.extend([self._fmt(score["hafalan"]), self._fmt(score["praktik"])])
                widths.extend([86, 86])
            values.append(self._fmt(row["rata_akhir"]))
            widths.append(100)
            for value, width in zip(values, widths):
                ctk.CTkLabel(item, text=value, width=width, anchor="w", font=(theme.FONT, 12), text_color=theme.TEXT).pack(
                    side="left", padx=9, pady=10
                )
        if len(detail["rows"]) > len(preview_rows):
            ctk.CTkLabel(
                card.body,
                text=f"Preview menampilkan {len(preview_rows)} dari {len(detail['rows'])} siswa. Export tetap memuat semua data.",
                font=(theme.FONT, 12, "bold"),
                text_color=theme.TEXT_MUTED,
                anchor="w",
            ).pack(fill="x", padx=16, pady=(8, 0))
        return card

    def _ranking_table(self, title: str, rows):
        card = SectionCard(self.body, title, "Urutan mengikuti rata-rata total, lalu tie-break hafalan, praktik, dan nama.")
        header = TableHeader(
            card.body,
            [("Rank", 70), ("NIS", 120), ("Nama", 260), ("Kelas", 90), ("Hafalan", 100), ("Praktik", 100), ("Total", 100), ("Status", 120)],
        )
        header.pack(fill="x", padx=0)
        for idx, row in enumerate(rows, start=1):
            item = TableRow(card.body, idx)
            item.pack(fill="x", pady=2)
            values = [
                "-" if row.peringkat is None else str(row.peringkat),
                row.nis,
                row.nama,
                row.kelas,
                self._fmt(row.rata_hafalan),
                self._fmt(row.rata_praktik),
                self._fmt(row.rata_total),
            ]
            widths = [70, 120, 260, 90, 100, 100, 100]
            for value, width in zip(values, widths):
                ctk.CTkLabel(item, text=value, width=width, anchor="w", font=(theme.FONT, 12), text_color=theme.TEXT).pack(
                    side="left", padx=10, pady=10
                )
            badge(item, row.status, row.status).pack(side="left", padx=10)
        return card

    def _mini_table(self, title: str, rows):
        card = SectionCard(self.body, title)
        for row in rows:
            ctk.CTkLabel(
                card.body,
                text=f"{row.peringkat}. {row.nama} - {self._fmt(row.rata_total)}",
                anchor="w",
                font=(theme.FONT, 13),
                text_color=theme.TEXT,
            ).pack(fill="x", padx=16, pady=6)
        return card

    def _fmt(self, value):
        return "-" if value is None else f"{value:.1f}"

    def _current_rekap_stats(self):
        kelas_id = self.kelas_map.get(self.kelas_var.get())
        if kelas_id is None:
            rekap = self.repo.get_rekap_semester(self.semester["id"])
            totals = [r.rata_total for r in rekap if r.rata_total is not None]
            stats = {
                "jumlah_siswa": len(rekap),
                "jumlah_materi": len(self.repo.list_materi(self.semester["id"])),
                "rata_kelas": None if not totals else sum(totals) / len(totals),
                "jumlah_lengkap": sum(1 for r in rekap if r.status == "lengkap"),
                "jumlah_sebagian": sum(1 for r in rekap if r.status == "sebagian"),
                "jumlah_belum": sum(1 for r in rekap if r.status == "belum"),
            }
            kelas_label = "Semua Kelas"
        else:
            rekap = self.repo.get_rekap_kelas(self.semester["id"], kelas_id)
            stats = self.repo.get_statistik_kelas(self.semester["id"], kelas_id)
            kelas_label = self.kelas_var.get()
        return rekap, stats, kelas_label

    def _metadata(self, kelas_label: str):
        return {
            "nama_sekolah": self.repo.get_pengaturan("nama_sekolah") or "MTs PIB",
            "tahun_ajaran": self.semester.get("tahun_ajaran", "-"),
            "semester": self.semester.get("nama", "-"),
            "kelas": kelas_label,
            "tanggal_export": date.today().isoformat(),
        }

    def export_excel(self):
        rekap, _, kelas_label = self._current_rekap_stats()
        kelas_id = self.kelas_map.get(self.kelas_var.get())
        detail = self.repo.get_laporan_detail(self.semester["id"], kelas_id)
        filename = f"PIB_{kelas_label.replace(' ', '_')}_{date.today().isoformat()}.xlsx"
        path = EXPORT_DIR / filename
        loading = show_loading(self, "Export Excel", "Menyusun workbook laporan...")
        try:
            result = export_laporan_excel(path, self._metadata(kelas_label), rekap, detail)
            loading.close()
            show_toast(self, "Export Excel berhasil", f"Tersimpan di {result}.")
        except Exception as exc:
            if loading.winfo_exists():
                loading.close()
            messagebox.showerror("Export gagal", str(exc))

    def export_pdf(self):
        rekap, stats, kelas_label = self._current_rekap_stats()
        kelas_id = self.kelas_map.get(self.kelas_var.get())
        detail = self.repo.get_laporan_detail(self.semester["id"], kelas_id)
        top, bottom = ambil_top_bottom(rekap, 5)
        filename = f"PIB_{kelas_label.replace(' ', '_')}_{date.today().isoformat()}.pdf"
        path = EXPORT_DIR / filename
        loading = show_loading(self, "Cetak PDF", "Menyusun dokumen laporan...")
        try:
            result = export_laporan_pdf(path, self._metadata(kelas_label), rekap, stats, top, bottom, detail)
            loading.close()
            show_toast(self, "PDF berhasil dibuat", f"Tersimpan di {result}.")
        except Exception as exc:
            if loading.winfo_exists():
                loading.close()
            messagebox.showerror("Export gagal", str(exc))

    def export_json_backup(self):
        EXPORT_DIR.mkdir(parents=True, exist_ok=True)
        default_name = f"pib-backup-{date.today().isoformat()}.json"
        path = filedialog.asksaveasfilename(
            title="Simpan Backup JSON",
            defaultextension=".json",
            initialdir=EXPORT_DIR,
            initialfile=default_name,
            filetypes=[("JSON Backup", "*.json")],
        )
        if not path:
            return
        loading = show_loading(self, "Backup JSON", "Mengumpulkan data aplikasi...")
        try:
            data = self.repo.backup_json_data()
            with open(path, "w", encoding="utf-8") as file:
                json.dump(data, file, ensure_ascii=False, indent=2)
            loading.close()
            show_toast(self, "Backup JSON berhasil", f"Tersimpan di {path}.")
        except Exception as exc:
            if loading.winfo_exists():
                loading.close()
            messagebox.showerror("Backup gagal", str(exc))

    def import_json_backup(self):
        path = filedialog.askopenfilename(
            title="Pilih Backup JSON",
            filetypes=[("JSON Backup", "*.json")],
        )
        if not path:
            return
        if not messagebox.askyesno(
            "Pulihkan backup?",
            "Import JSON akan mengganti seluruh data desktop saat ini dengan isi backup. Lanjutkan?",
        ):
            return
        loading = show_loading(self, "Import JSON", "Memulihkan data backup...")
        try:
            with open(path, "r", encoding="utf-8") as file:
                data = json.load(file)
            self.repo.restore_json_data(data)
            loading.close()
            show_toast(self, "Backup dipulihkan", "Data aplikasi berhasil diganti dari file JSON.", "success")
            self.refresh_callback()
        except Exception as exc:
            if loading.winfo_exists():
                loading.close()
            messagebox.showerror("Import gagal", str(exc))
