from __future__ import annotations

from datetime import datetime
from tkinter import messagebox

import customtkinter as ctk

from models.penilaian import PenilaianInput
from services.penilaian_service import hitung_nilai, hitung_rata_total
from ui import theme
from ui.components.widgets import (
    EmptyState,
    SectionCard,
    StatCard,
    TableHeader,
    TableRow,
    primary_button,
    secondary_button,
    show_loading,
    show_toast,
    styled_option,
)

KKM_TUNTAS = 75


class PenilaianView(ctk.CTkFrame):
    def __init__(self, master, repo, refresh_callback):
        super().__init__(master, fg_color=theme.BACKGROUND)
        self.repo = repo
        self.refresh_callback = refresh_callback
        self.semester = repo.get_semester_aktif()
        self.kelas_list = repo.list_kelas()
        self.kelas_map = {k["nama"]: k["id"] for k in self.kelas_list}
        self.materi_names = repo.list_nama_materi(self.semester["id"]) if self.semester else []
        self.kelas_var = ctk.StringVar(value=self.kelas_list[0]["nama"] if self.kelas_list else "")
        self.materi_var = ctk.StringVar(value=self.materi_names[0] if self.materi_names else "")
        self.entry_vars: dict[tuple[int, str], ctk.StringVar] = {}
        self.preview_labels: dict[tuple[int, str], ctk.CTkLabel] = {}
        self.rata_labels: dict[int, ctk.CTkLabel] = {}
        self.ketuntasan_labels: dict[int, ctk.CTkLabel] = {}
        self.touched_entries: set[tuple[int, str]] = set()
        self.grid_columnconfigure(0, weight=1)

        hero = ctk.CTkFrame(self, fg_color=theme.SURFACE_ACCENT, border_color=theme.BORDER, border_width=1, corner_radius=12)
        hero.grid(row=0, column=0, sticky="ew", pady=(0, 18))
        hero.grid_columnconfigure(0, weight=1)
        ctk.CTkLabel(hero, text="Input Penilaian PIB", font=(theme.FONT, 26, "bold"), text_color=theme.TEXT).grid(
            row=0, column=0, sticky="w", padx=20, pady=(18, 4)
        )
        ctk.CTkLabel(
            hero,
            text="Pilih satu materi dan kelas, lalu isi jumlah kesalahan Hafalan dan Praktik per siswa.",
            font=(theme.FONT, 14),
            text_color=theme.TEXT_MUTED,
        ).grid(row=1, column=0, sticky="w", padx=20, pady=(0, 18))

        if not self.semester or not self.kelas_list:
            EmptyState(self, "Data awal belum lengkap", "Buat semester aktif dan kelas sebelum mengisi penilaian.").grid(
                row=1, column=0, sticky="ew"
            )
            return
        if not self.materi_names:
            EmptyState(self, "Belum ada materi aktif", "Tambahkan materi di menu Materi sebelum mengisi penilaian.").grid(
                row=1, column=0, sticky="ew"
            )
            return

        self._toolbar().grid(row=1, column=0, sticky="ew", pady=(0, 18))
        self.stats_frame = ctk.CTkFrame(self, fg_color=theme.BACKGROUND)
        self.stats_frame.grid(row=2, column=0, sticky="ew", pady=(0, 18))
        self.stats_frame.grid_columnconfigure((0, 1, 2, 3), weight=1)
        self.table_frame = SectionCard(
            self,
            "Lembar Penilaian Per Materi",
            "Kolom Hafalan dan Praktik berisi jumlah kesalahan. Nilai akhir dihitung otomatis.",
        )
        self.table_frame.grid(row=3, column=0, sticky="nsew")
        self.load_table()

    def _toolbar(self):
        bar = ctk.CTkFrame(self, fg_color=theme.SURFACE, border_color=theme.BORDER, border_width=1, corner_radius=theme.RADIUS)
        bar.grid_columnconfigure(1, weight=1)
        bar.grid_columnconfigure(3, weight=1)

        ctk.CTkLabel(bar, text="Nama Materi", font=(theme.FONT, 13, "bold"), text_color=theme.TEXT).grid(
            row=0, column=0, sticky="w", padx=(16, 8), pady=(12, 4)
        )
        ctk.CTkLabel(bar, text="Kelas", font=(theme.FONT, 13, "bold"), text_color=theme.TEXT).grid(
            row=0, column=2, sticky="w", padx=(16, 8), pady=(12, 4)
        )
        self._option_menu(bar, self.materi_names, self.materi_var).grid(row=1, column=0, columnspan=2, sticky="ew", padx=(16, 8), pady=(0, 14))
        self._option_menu(bar, list(self.kelas_map), self.kelas_var).grid(row=1, column=2, columnspan=2, sticky="ew", padx=(8, 16), pady=(0, 14))
        secondary_button(bar, "Refresh", command=self.load_table, width=110).grid(row=1, column=4, padx=(0, 8), pady=(0, 14))
        primary_button(bar, "Simpan", command=self.save_table, width=120).grid(row=1, column=5, padx=(0, 16), pady=(0, 14))
        return bar

    def _option_menu(self, master, values: list[str], variable: ctk.StringVar):
        return styled_option(master, values, variable, command=lambda _: self.load_table())

    def load_table(self):
        for child in self.stats_frame.winfo_children():
            child.destroy()
        for child in self.table_frame.body.winfo_children():
            child.destroy()
        self.entry_vars.clear()
        self.preview_labels.clear()
        self.rata_labels.clear()
        self.ketuntasan_labels.clear()
        self.touched_entries.clear()

        kelas_id = self.kelas_map.get(self.kelas_var.get())
        nama_materi = self.materi_var.get()
        if not kelas_id or not nama_materi:
            return

        self.repo.ensure_materi_pair_by_nama(self.semester["id"], nama_materi)
        self.data = self.repo.get_penilaian_materi_kelas(self.semester["id"], kelas_id, nama_materi)
        self.siswa_list = self.data["siswa_list"]
        self.materi_pair = self.data["materi_pair"]
        self.penilaian_map = self.data["penilaian_map"]

        rows_preview = self._collect_existing_previews()
        sudah = sum(1 for item in rows_preview if item["rata"] is not None)
        belum_tuntas = sum(1 for item in rows_preview if item["rata"] is not None and item["rata"] < KKM_TUNTAS)
        rata_values = [item["rata"] for item in rows_preview if item["rata"] is not None]
        rata_kelas = None if not rata_values else sum(rata_values) / len(rata_values)

        cards = [
            ("Total Siswa", str(len(self.siswa_list)), "#84E9DD", "S"),
            ("Sudah Dinilai", str(sudah), "#D0E1FB", "N"),
            ("Rata-rata Kelas", "-" if rata_kelas is None else f"{rata_kelas:.1f}", "#E0E3E5", "R"),
            ("Belum Tuntas", str(belum_tuntas), "#FFDAD6", "!"),
        ]
        for i, (title, value, accent, icon) in enumerate(cards):
            StatCard(self.stats_frame, title, value, accent, icon=icon).grid(row=0, column=i, sticky="ew", padx=(0 if i == 0 else 10, 0))

        if not self.siswa_list:
            EmptyState(self.table_frame.body, "Belum ada siswa", "Tambahkan siswa pada kelas ini sebelum mengisi nilai.").pack(
                fill="x", padx=18, pady=(0, 18)
            )
            return

        missing = [aspek for aspek in ("hafalan", "praktik") if aspek not in self.materi_pair]
        if missing:
            info = ctk.CTkFrame(self.table_frame.body, fg_color=theme.WARNING_BG, corner_radius=6)
            info.pack(fill="x", padx=18, pady=(0, 12))
            ctk.CTkLabel(
                info,
                text=f"Aspek belum lengkap untuk materi ini: {', '.join(missing)}. Tambahkan pasangan aspek di menu Materi.",
                font=(theme.FONT, 12, "bold"),
                text_color=theme.WARNING_TEXT,
                anchor="w",
                wraplength=900,
                justify="left",
            ).pack(fill="x", padx=14, pady=10)

        self._header_row().pack(fill="x", padx=18)
        for index, siswa in enumerate(self.siswa_list, start=1):
            self._student_row(index, siswa).pack(fill="x", padx=18, pady=3)

    def _header_row(self):
        columns = [
            ("No", 48),
            ("Nama Siswa", 220),
            ("Hafalan", 110),
            ("Nilai Hafalan", 110),
            ("Praktik", 110),
            ("Nilai Praktik", 110),
            ("Rata-rata", 100),
            ("Ketuntasan", 130),
        ]
        return TableHeader(self.table_frame.body, columns)

    def _student_row(self, index: int, siswa: dict):
        row = TableRow(self.table_frame.body, index)
        ctk.CTkLabel(row, text=str(index), width=48, anchor="w", font=(theme.FONT, 13), text_color=theme.TEXT).pack(side="left", padx=8, pady=8)
        ctk.CTkLabel(row, text=siswa["nama"], width=220, anchor="w", font=(theme.FONT, 13, "bold"), text_color=theme.TEXT).pack(
            side="left", padx=8, pady=8
        )
        for aspek in ("hafalan", "praktik"):
            existing = self.penilaian_map.get((siswa["id"], aspek))
            var = ctk.StringVar(value="" if existing is None else str(existing["jumlah_kesalahan"]))
            self.entry_vars[(siswa["id"], aspek)] = var
            self._error_stepper(row, siswa["id"], aspek, var).pack(side="left", padx=8, pady=8)
            nilai_label = ctk.CTkLabel(row, text="-", width=110, anchor="center", font=(theme.FONT, 13, "bold"), text_color=theme.PRIMARY)
            nilai_label.pack(side="left", padx=8, pady=8)
            self.preview_labels[(siswa["id"], aspek)] = nilai_label
            var.trace_add("write", lambda *_args, siswa_id=siswa["id"]: self._update_row_preview(siswa_id))

        rata_label = ctk.CTkLabel(row, text="-", width=100, anchor="center", font=(theme.FONT, 13, "bold"), text_color=theme.TEXT)
        rata_label.pack(side="left", padx=8, pady=8)
        self.rata_labels[siswa["id"]] = rata_label
        ketuntasan_label = ctk.CTkLabel(row, text="-", width=130, anchor="center", font=(theme.FONT, 12, "bold"), corner_radius=999)
        ketuntasan_label.pack(side="left", padx=8, pady=8)
        self.ketuntasan_labels[siswa["id"]] = ketuntasan_label
        self._update_row_preview(siswa["id"])
        return row

    def _error_stepper(self, master, siswa_id: int, aspek: str, var: ctk.StringVar):
        enabled = aspek in self.materi_pair
        frame = ctk.CTkFrame(master, width=110, height=46, fg_color=theme.SURFACE, border_color=theme.BORDER, border_width=1, corner_radius=theme.RADIUS)
        frame.pack_propagate(False)
        frame.grid_columnconfigure(0, weight=1)

        value = ctk.CTkLabel(frame, textvariable=var, width=48, anchor="center", font=(theme.FONT, 14, "bold"), text_color=theme.TEXT)
        value.grid(row=0, column=0, rowspan=2, sticky="nsew", padx=(6, 2), pady=4)

        up = ctk.CTkButton(
            frame,
            text="+",
            width=42,
            height=20,
            fg_color=theme.PRIMARY if enabled else theme.BORDER,
            hover_color=theme.PRIMARY_HOVER if enabled else theme.BORDER,
            text_color="white" if enabled else theme.TEXT_MUTED,
            font=(theme.FONT, 10, "bold"),
            command=lambda: self._step_error(siswa_id, aspek, 1),
            state="normal" if enabled else "disabled",
        )
        up.grid(row=0, column=1, sticky="ew", padx=(2, 4), pady=(4, 1))

        down = ctk.CTkButton(
            frame,
            text="-",
            width=42,
            height=20,
            fg_color=theme.SURFACE_LOW if enabled else theme.BORDER,
            hover_color=theme.PRIMARY_SOFT if enabled else theme.BORDER,
            text_color=theme.TEXT if enabled else theme.TEXT_MUTED,
            font=(theme.FONT, 10, "bold"),
            command=lambda: self._step_error(siswa_id, aspek, -1),
            state="normal" if enabled else "disabled",
        )
        down.grid(row=1, column=1, sticky="ew", padx=(2, 4), pady=(1, 4))

        if var.get().strip() == "":
            var.set("0" if enabled else "")
        return frame

    def _step_error(self, siswa_id: int, aspek: str, delta: int) -> None:
        var = self.entry_vars.get((siswa_id, aspek))
        if not var:
            return
        self.touched_entries.add((siswa_id, aspek))
        try:
            current = int(var.get().strip() or "0")
        except ValueError:
            current = 0
        var.set(str(max(0, current + delta)))

    def _nilai_from_var(self, siswa_id: int, aspek: str) -> float | None:
        materi = self.materi_pair.get(aspek)
        var = self.entry_vars.get((siswa_id, aspek))
        if not materi or not var:
            return None
        raw = var.get().strip()
        if raw == "":
            return None
        try:
            jumlah = int(raw)
            if jumlah < 0:
                return None
        except ValueError:
            return None
        return hitung_nilai(jumlah, materi["poin_pengurangan"])

    def _update_row_preview(self, siswa_id: int) -> None:
        nilai_hafalan = self._nilai_from_var(siswa_id, "hafalan")
        nilai_praktik = self._nilai_from_var(siswa_id, "praktik")
        for aspek, nilai in [("hafalan", nilai_hafalan), ("praktik", nilai_praktik)]:
            label = self.preview_labels.get((siswa_id, aspek))
            if label:
                label.configure(text="-" if nilai is None else f"{nilai:.1f}")
        rata = hitung_rata_total(nilai_hafalan, nilai_praktik)
        if siswa_id in self.rata_labels:
            self.rata_labels[siswa_id].configure(text="-" if rata is None else f"{rata:.1f}")
        if siswa_id in self.ketuntasan_labels:
            label = self.ketuntasan_labels[siswa_id]
            if rata is None:
                label.configure(text="Belum Dinilai", fg_color=theme.SURFACE_LOW, text_color=theme.TEXT_MUTED)
            elif rata >= KKM_TUNTAS:
                label.configure(text="Tuntas", fg_color=theme.SUCCESS_BG, text_color=theme.SUCCESS_TEXT)
            else:
                label.configure(text="Belum Tuntas", fg_color=theme.ERROR_BG, text_color=theme.ERROR_TEXT)

    def _collect_row_previews(self) -> list[dict]:
        result = []
        for siswa in getattr(self, "siswa_list", []):
            nilai_hafalan = self._nilai_from_var(siswa["id"], "hafalan")
            nilai_praktik = self._nilai_from_var(siswa["id"], "praktik")
            result.append({"siswa_id": siswa["id"], "rata": hitung_rata_total(nilai_hafalan, nilai_praktik)})
        return result

    def _collect_existing_previews(self) -> list[dict]:
        result = []
        for siswa in getattr(self, "siswa_list", []):
            hafalan = self.penilaian_map.get((siswa["id"], "hafalan"))
            praktik = self.penilaian_map.get((siswa["id"], "praktik"))
            nilai_hafalan = None if hafalan is None else hafalan["nilai"]
            nilai_praktik = None if praktik is None else praktik["nilai"]
            result.append({"siswa_id": siswa["id"], "rata": hitung_rata_total(nilai_hafalan, nilai_praktik)})
        return result

    def save_table(self):
        if not hasattr(self, "siswa_list"):
            return
        records = []
        try:
            for siswa in self.siswa_list:
                for aspek in ("hafalan", "praktik"):
                    materi = self.materi_pair.get(aspek)
                    if not materi:
                        continue
                    existing = self.penilaian_map.get((siswa["id"], aspek))
                    raw = self.entry_vars[(siswa["id"], aspek)].get().strip()
                    if raw == "":
                        continue
                    if existing is None and (siswa["id"], aspek) not in self.touched_entries:
                        continue
                    jumlah = int(raw)
                    PenilaianInput(siswa_id=siswa["id"], materi_id=materi["id"], jumlah_kesalahan=jumlah)
                    records.append(
                        {
                            "siswa_id": siswa["id"],
                            "materi_id": materi["id"],
                            "jumlah_kesalahan": jumlah,
                            "nilai": hitung_nilai(jumlah, materi["poin_pengurangan"]),
                            "poin_snapshot": materi["poin_pengurangan"],
                            "updated_at": datetime.now().isoformat(timespec="seconds"),
                        }
                    )
        except Exception as exc:
            messagebox.showerror("Input tidak valid", f"Pastikan semua kesalahan berupa angka 0 atau lebih.\n\n{exc}")
            return

        loading = show_loading(self, "Menyimpan penilaian", "Menghitung nilai dan memperbarui data siswa...")
        try:
            self.repo.upsert_penilaian_batch(records)
        finally:
            loading.close()
        show_toast(self, "Penilaian disimpan", f"{len(records)} nilai berhasil diperbarui.")
        self.load_table()
