from __future__ import annotations

import customtkinter as ctk

from ui import theme
from ui.components.widgets import EmptyState, ModernPanel, PageHero, StatCard, TableRow, badge, primary_button, secondary_button


class DashboardView(ctk.CTkFrame):
    def __init__(self, master, repo, refresh_callback):
        super().__init__(master, fg_color=theme.BACKGROUND)
        self.repo = repo
        self.refresh_callback = refresh_callback
        self.grid_columnconfigure((0, 1), weight=1)

        semester = repo.get_semester_aktif()
        kelas_list = repo.list_kelas()
        sekolah = repo.get_pengaturan("nama_sekolah") or "MTs PIB"
        periode_label = "Belum ada periode aktif"
        if semester:
            periode_label = f"{semester['nama']} {semester['tahun_ajaran']}"

        PageHero(
            self,
            "Dashboard",
            f"Ruang Kerja {sekolah}",
            f"Periode {periode_label}. Pantau progres, lanjutkan input nilai, dan siapkan laporan dari satu layar.",
            "Offline",
            "aktif",
        ).grid(row=0, column=0, columnspan=2, sticky="ew", pady=(0, 22))

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
        sudah_dinilai = sum(1 for r in rekap if r.rata_total is not None)
        progress = 0 if not siswa else sudah_dinilai / len(siswa)

        cards = [
            ("Total Siswa", str(len(siswa)), theme.ACCENT_MINT, "S", "semester ini"),
            ("Total Materi", str(len(materi)), theme.ACCENT_BLUE, "M", "aktif"),
            ("Rata-rata Nilai", "-" if rata is None else f"{rata:.1f}", theme.PRIMARY_SOFT_2, "N", "kelas"),
            ("Belum Lengkap", str(belum_lengkap), theme.ERROR_BG, "!", "perlu cek"),
        ]
        for i, (title, value, accent, icon, note) in enumerate(cards):
            StatCard(self, title, value, accent, icon=icon, note=note).grid(
                row=1 + (i // 2),
                column=i % 2,
                sticky="ew",
                padx=(0, 10) if i % 2 == 0 else (10, 0),
                pady=(0, 16),
            )

        action_panel = ModernPanel(self, "Mulai dari Sini", "Aksi cepat berdasarkan pekerjaan guru yang paling sering dilakukan.")
        action_panel.grid(row=3, column=0, columnspan=2, sticky="ew", pady=(4, 18))
        action_panel.body.grid_columnconfigure((0, 1, 2), weight=1)
        self._quick_action(action_panel.body, "Input Nilai", "Lanjutkan penilaian siswa.", "Penilaian", primary=True).grid(
            row=0, column=0, sticky="ew", padx=(18, 8), pady=(2, 4)
        )
        self._quick_action(action_panel.body, "Kelola Siswa", "Tambah atau import data siswa.", "Siswa").grid(
            row=0, column=1, sticky="ew", padx=8, pady=(2, 4)
        )
        self._quick_action(action_panel.body, "Cetak Laporan", "Export PDF atau Excel.", "Laporan").grid(
            row=0, column=2, sticky="ew", padx=(8, 18), pady=(2, 4)
        )

        progress_panel = ModernPanel(self, "Efektivitas Semester", "Ringkasan cepat pekerjaan yang sudah dan belum selesai.")
        progress_panel.grid(row=4, column=0, columnspan=2, sticky="ew", pady=(0, 18))
        progress_panel.body.grid_columnconfigure(0, weight=1)
        ctk.CTkLabel(
            progress_panel.body,
            text=f"{progress * 100:.0f}% siswa sudah memiliki nilai",
            font=(theme.FONT, 16, "bold"),
            text_color=theme.TEXT,
            anchor="w",
        ).grid(row=0, column=0, sticky="ew", padx=20, pady=(2, 8))
        bar = ctk.CTkProgressBar(progress_panel.body, progress_color=theme.ACCENT_MINT, fg_color=theme.DIVIDER, height=16)
        bar.grid(row=1, column=0, sticky="ew", padx=20, pady=(0, 14))
        bar.set(progress)
        ctk.CTkLabel(
            progress_panel.body,
            text=f"{sudah_dinilai} dari {len(siswa)} siswa sudah dinilai. {belum_lengkap} siswa masih perlu dilengkapi.",
            font=(theme.FONT, 13),
            text_color=theme.TEXT_MUTED,
            anchor="w",
        ).grid(row=2, column=0, sticky="ew", padx=20, pady=(0, 6))

        panel = ModernPanel(self, "Peringkat Terbaik", "Lima siswa dengan rata-rata total tertinggi.")
        panel.grid(row=5, column=0, sticky="nsew", padx=(0, 12), pady=(0, 0))
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

        attention = ModernPanel(self, "Perlu Perhatian", "Siswa bernilai terendah dari data yang sudah dinilai.")
        attention.grid(row=5, column=1, sticky="nsew", padx=(12, 0), pady=(0, 0))
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

        kelas_panel = ModernPanel(self, "Monitoring Kelas", "Progres kelengkapan penilaian per kelas.")
        kelas_panel.grid(row=6, column=0, columnspan=2, sticky="ew", pady=(24, 0))
        for kelas in kelas_list:
            stats = repo.get_statistik_kelas(semester["id"], kelas["id"])
            progress = 0 if stats["jumlah_siswa"] == 0 else stats["jumlah_lengkap"] / stats["jumlah_siswa"]
            row = TableRow(kelas_panel.body, kelas["id"])
            row.pack(fill="x", padx=18, pady=6)
            ctk.CTkLabel(row, text=f"Kelas {kelas['nama']}", font=(theme.FONT, 14, "bold"), width=120, anchor="w").pack(side="left", padx=(12, 0), pady=12)
            ctk.CTkProgressBar(row, progress_color=theme.PRIMARY, fg_color=theme.DIVIDER, width=220).pack(side="left", padx=16)
            row.winfo_children()[1].set(progress)
            ctk.CTkLabel(row, text=f"{progress * 100:.0f}% lengkap", text_color=theme.TEXT_MUTED).pack(side="left")

    def _quick_action(self, master, title: str, subtitle: str, target: str, primary: bool = False):
        card = ctk.CTkFrame(master, fg_color=theme.SURFACE_RAISED, border_color=theme.BORDER, border_width=1, corner_radius=20)
        card.grid_columnconfigure(0, weight=1)
        ctk.CTkLabel(card, text=title, font=(theme.FONT, 16, "bold"), text_color=theme.TEXT, anchor="w").grid(
            row=0, column=0, sticky="ew", padx=16, pady=(14, 2)
        )
        ctk.CTkLabel(card, text=subtitle, font=(theme.FONT, 12), text_color=theme.TEXT_MUTED, anchor="w").grid(
            row=1, column=0, sticky="ew", padx=16, pady=(0, 12)
        )
        button_factory = primary_button if primary else secondary_button
        button_factory(card, f"Buka {target}", command=lambda: self._go_to(target)).grid(
            row=2, column=0, sticky="ew", padx=16, pady=(0, 16)
        )
        return card

    def _go_to(self, target: str) -> None:
        root = self.winfo_toplevel()
        if hasattr(root, "show_view"):
            root.show_view(target)
