from __future__ import annotations

from datetime import date
from tkinter import messagebox

import customtkinter as ctk

from database.repository import Repository
from ui import theme
from ui.components.widgets import primary_button, styled_entry, styled_option


class FirstRunWizard(ctk.CTkToplevel):
    def __init__(self, master, repo: Repository, on_complete):
        super().__init__(master)
        self.repo = repo
        self.on_complete = on_complete
        self.title("Setup Awal PIB")
        self.geometry("620x680")
        self.minsize(560, 640)
        self.resizable(True, True)
        self.grab_set()

        year = date.today().year
        self.nama_sekolah = ctk.StringVar(value="MTs Al-Hikmah")
        self.tahun_ajaran = ctk.StringVar(value=f"{year}/{year + 1}")
        self.semester = ctk.StringVar(value="Ganjil")
        self.kelas_text = ctk.StringVar(value="7A, 7B, 8A")

        frame = ctk.CTkFrame(self, fg_color=theme.BACKGROUND)
        frame.pack(fill="both", expand=True)
        card = ctk.CTkFrame(frame, fg_color=theme.SURFACE, border_color=theme.BORDER, border_width=1, corner_radius=theme.RADIUS_LG)
        card.pack(fill="both", expand=True, padx=28, pady=28)
        card.grid_columnconfigure(0, weight=1)
        card.grid_rowconfigure(1, weight=1)

        header = ctk.CTkFrame(card, fg_color=theme.SURFACE)
        header.grid(row=0, column=0, sticky="ew", padx=28, pady=(28, 0))
        ctk.CTkLabel(header, text="Setup Awal Aplikasi", font=(theme.FONT, 24, "bold"), text_color=theme.TEXT).pack(
            anchor="w"
        )
        ctk.CTkLabel(
            header,
            text="Isi data dasar sekali saja. Nanti semua bisa diedit dari menu Periode.",
            font=(theme.FONT, 13),
            text_color=theme.TEXT_MUTED,
            wraplength=460,
        ).pack(anchor="w", pady=(6, 22))

        form = ctk.CTkFrame(card, fg_color=theme.SURFACE)
        form.grid(row=1, column=0, sticky="nsew", padx=28)
        self._field(form, "Nama Sekolah", self.nama_sekolah)
        self._field(form, "Tahun Ajaran", self.tahun_ajaran)
        ctk.CTkLabel(form, text="Semester", font=(theme.FONT, 13, "bold"), text_color=theme.TEXT).pack(
            anchor="w", pady=(12, 6)
        )
        styled_option(form, ["Ganjil", "Genap"], self.semester).pack(fill="x")
        self._field(form, "Kelas Awal (pisahkan dengan koma)", self.kelas_text)

        action_bar = ctk.CTkFrame(card, fg_color=theme.SURFACE)
        action_bar.grid(row=2, column=0, sticky="ew", padx=28, pady=(18, 28))
        primary_button(action_bar, "Simpan dan Mulai", command=self._save).pack(fill="x")

    def _field(self, parent, label: str, variable: ctk.StringVar) -> None:
        ctk.CTkLabel(parent, text=label, font=(theme.FONT, 13, "bold"), text_color=theme.TEXT).pack(
            anchor="w", pady=(12, 6)
        )
        styled_entry(parent, variable).pack(fill="x")

    def _save(self) -> None:
        nama_sekolah = self.nama_sekolah.get().strip()
        tahun_ajaran = self.tahun_ajaran.get().strip()
        kelas_names = [k.strip().upper() for k in self.kelas_text.get().split(",") if k.strip()]
        if not nama_sekolah or "/" not in tahun_ajaran or not kelas_names:
            messagebox.showerror("Data belum lengkap", "Nama sekolah, tahun ajaran, dan minimal satu kelas wajib diisi.")
            return

        try:
            self.repo.set_pengaturan("nama_sekolah", nama_sekolah)
            ta_id = self.repo.create_tahun_ajaran(tahun_ajaran)
            self.repo.set_tahun_ajaran_aktif(ta_id)
            semester_id = self.repo.create_semester(ta_id, self.semester.get())
            self.repo.set_semester_aktif(semester_id)
            for kelas in kelas_names:
                tingkat = int(kelas[0]) if kelas[0].isdigit() else 7
                self.repo.create_kelas(kelas, tingkat)
        except Exception as exc:
            messagebox.showerror("Setup gagal", str(exc))
            return

        self.destroy()
        self.on_complete()
