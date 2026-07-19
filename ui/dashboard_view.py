from __future__ import annotations

import customtkinter as ctk

from ui import theme
from ui.components.widgets import EmptyState, SectionCard, StatCard, TableRow, badge


class DashboardView(ctk.CTkFrame):
    def __init__(self, master, repo, refresh_callback):
        super().__init__(master, fg_color=theme.BACKGROUND)
        self.repo = repo
        self.grid_columnconfigure((0, 1), weight=1)

        hero = ctk.CTkFrame(self, fg_color=theme.SURFACE_ACCENT, border_color=theme.BORDER, border_width=1, corner_radius=12)
        hero.grid(row=0, column=0, columnspan=2, sticky="ew", pady=(0, 22))
        hero.grid_columnconfigure(0, weight=1)
        ctk.CTkLabel(hero, text="Ringkasan Dashboard", font=(theme.FONT, 28, "bold"), text_color=theme.TEXT).grid(
            row=0, column=0, sticky="w", padx=22, pady=(20, 2)
        )
        ctk.CTkLabel(
            hero,
            text="Pantau progres penilaian PIB berdasarkan semester aktif.",
            font=(theme.FONT, 14),
            text_color=theme.TEXT_MUTED,
        ).grid(row=1, column=0, sticky="w", padx=22, pady=(0, 20))
        ctk.CTkLabel(
            hero,
            text="Offline",
            fg_color=theme.PRIMARY,
            text_color=theme.SURFACE,
            corner_radius=999,
            padx=12,
            height=28,
            font=(theme.FONT, 12, "bold"),
        ).grid(row=0, column=1, rowspan=2, padx=22, pady=22)

        semester = repo.get_semester_aktif()
        kelas_list = repo.list_kelas()
        if not semester:
            EmptyState(self, "Belum ada periode aktif", "Selesaikan setup awal untuk mulai mengelola data.").grid(
                row=1, column=0, columnspan=2, sticky="ew"
            )
            return

        siswa = repo.list_siswa(semester["id"])
        materi = repo.list_materi(semester["id"])
        rekap = repo.get_rekap_semester(semester["id"])
        totals = [r.rata_total for r in rekap if r.rata_total is not None]
        rata = sum(totals) / len(totals) if totals else None
        belum_lengkap = sum(1 for r in rekap if r.status != "lengkap")

        cards = [
            ("Total Siswa", str(len(siswa)), "#84E9DD", "S", "semester ini"),
            ("Total Materi", str(len(materi)), "#D0E1FB", "M", "aktif"),
            ("Rata-rata Nilai", "-" if rata is None else f"{rata:.1f}", "#E0E3E5", "N", "kelas"),
            ("Belum Lengkap", str(belum_lengkap), "#FFDAD6", "!", "perlu cek"),
        ]
        for i, (title, value, accent, icon, note) in enumerate(cards):
            StatCard(self, title, value, accent, icon=icon, note=note).grid(
                row=1 + (i // 2),
                column=i % 2,
                sticky="ew",
                padx=(0, 10) if i % 2 == 0 else (10, 0),
                pady=(0, 16),
            )

        panel = SectionCard(self, "Peringkat Terbaik", "Lima siswa dengan rata-rata total tertinggi.")
        panel.grid(row=3, column=0, sticky="nsew", padx=(0, 12), pady=(8, 0))
        panel.body.grid_columnconfigure(0, weight=1)
        top = [r for r in rekap if r.peringkat is not None][:5]
        if not top:
            ctk.CTkLabel(panel.body, text="Belum ada nilai tersimpan.", text_color=theme.TEXT_MUTED).grid(
                row=1, column=0, sticky="w", padx=20, pady=(0, 18)
            )
        else:
            for idx, row in enumerate(top, start=1):
                line = TableRow(panel.body, idx)
                line.grid(row=idx, column=0, columnspan=2, sticky="ew", padx=18, pady=4)
                line.grid_columnconfigure(0, weight=1)
                ctk.CTkLabel(
                    line,
                    text=f"{row.peringkat}. {row.nama} ({row.kelas})",
                    font=(theme.FONT, 14, "bold"),
                    text_color=theme.TEXT,
                    anchor="w",
                ).grid(row=0, column=0, sticky="ew", padx=12, pady=10)
                ctk.CTkLabel(
                    line,
                    text=f"{row.rata_total:.1f}",
                    font=(theme.FONT, 14, "bold"),
                    text_color=theme.PRIMARY,
                ).grid(row=0, column=1, padx=12, pady=10)

        attention = SectionCard(self, "Perlu Perhatian", "Siswa bernilai terendah dari data yang sudah dinilai.")
        attention.grid(row=3, column=1, sticky="nsew", padx=(12, 0), pady=(8, 0))
        bottom = list(reversed([r for r in rekap if r.peringkat is not None][-5:]))
        if not bottom:
            ctk.CTkLabel(attention.body, text="Belum ada data untuk dianalisis.", text_color=theme.TEXT_MUTED).pack(
                anchor="w", padx=18, pady=(0, 18)
            )
        for row in bottom:
            item = TableRow(attention.body, row.peringkat or 0)
            item.pack(fill="x", padx=18, pady=4)
            ctk.CTkLabel(item, text=row.nama, anchor="w", font=(theme.FONT, 13, "bold"), text_color=theme.TEXT).pack(
                side="left", fill="x", expand=True, padx=12, pady=10
            )
            badge(item, f"{row.rata_total:.1f}", "gold").pack(side="right", padx=10)

        kelas_panel = SectionCard(self, "Monitoring Kelas", "Progres kelengkapan penilaian per kelas.")
        kelas_panel.grid(row=4, column=0, columnspan=2, sticky="ew", pady=(24, 0))
        for kelas in kelas_list:
            stats = repo.get_statistik_kelas(semester["id"], kelas["id"])
            progress = 0 if stats["jumlah_siswa"] == 0 else stats["jumlah_lengkap"] / stats["jumlah_siswa"]
            row = TableRow(kelas_panel.body, kelas["id"])
            row.pack(fill="x", padx=18, pady=6)
            ctk.CTkLabel(row, text=f"Kelas {kelas['nama']}", font=(theme.FONT, 14, "bold"), width=120, anchor="w").pack(side="left", padx=(12, 0), pady=12)
            ctk.CTkProgressBar(row, progress_color=theme.PRIMARY, fg_color=theme.DIVIDER, width=220).pack(side="left", padx=16)
            row.winfo_children()[1].set(progress)
            ctk.CTkLabel(row, text=f"{progress * 100:.0f}% lengkap", text_color=theme.TEXT_MUTED).pack(side="left")
