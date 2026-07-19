from __future__ import annotations

from tkinter import messagebox

import customtkinter as ctk

from ui import theme
from ui.components.widgets import SectionCard, badge, danger_button, primary_button, secondary_button, show_toast, styled_entry, styled_option


class PeriodeView(ctk.CTkFrame):
    def __init__(self, master, repo, refresh_callback):
        super().__init__(master, fg_color=theme.BACKGROUND)
        self.repo = repo
        self.refresh_callback = refresh_callback
        self.editing_kelas_id: int | None = None
        self.grid_columnconfigure((0, 1), weight=1)

        hero = ctk.CTkFrame(self, fg_color=theme.SURFACE_ACCENT, border_color=theme.BORDER, border_width=1, corner_radius=12)
        hero.grid(row=0, column=0, columnspan=2, sticky="ew", pady=(0, 18))
        ctk.CTkLabel(hero, text="Periode dan Kelas", font=(theme.FONT, 26, "bold"), text_color=theme.TEXT).pack(
            anchor="w", padx=20, pady=(18, 4)
        )
        ctk.CTkLabel(
            hero,
            text="Atur tahun ajaran, semester aktif, dan daftar kelas yang akan dipakai saat penilaian.",
            font=(theme.FONT, 14),
            text_color=theme.TEXT_MUTED,
        ).pack(anchor="w", padx=20, pady=(0, 18))
        self._periode_card().grid(row=1, column=0, sticky="nsew", padx=(0, 12))
        self._kelas_card().grid(row=1, column=1, sticky="nsew", padx=(12, 0))

    def _periode_card(self):
        card = SectionCard(self, "Tahun Ajaran dan Semester", "Buat tahun ajaran baru, pilih semester, lalu jadikan periode aktif.")
        ta_var = ctk.StringVar(value="2026/2027")
        sem_var = ctk.StringVar(value="Ganjil")
        self._labeled_entry(card.body, "Tahun Ajaran", "Contoh: 2026/2027", ta_var)
        self._labeled_option(card.body, "Semester", ["Ganjil", "Genap"], sem_var)

        def save():
            try:
                ta_id = self.repo.create_tahun_ajaran(ta_var.get().strip())
                self.repo.set_tahun_ajaran_aktif(ta_id)
                sem_id = self.repo.create_semester(ta_id, sem_var.get())
                self.repo.set_semester_aktif(sem_id)
                show_toast(self, "Periode aktif disimpan", f"{sem_var.get()} {ta_var.get().strip()} siap digunakan.")
                self.refresh_callback()
            except Exception as exc:
                messagebox.showerror("Gagal menyimpan periode", str(exc))

        primary_button(card.body, "Simpan sebagai Periode Aktif", command=save).pack(fill="x", padx=18, pady=(12, 18))
        ctk.CTkLabel(
            card.body,
            text="Periode Tersimpan",
            font=(theme.FONT, 13, "bold"),
            text_color=theme.TEXT_MUTED,
            anchor="w",
        ).pack(fill="x", padx=18, pady=(0, 6))
        for ta in self.repo.list_tahun_ajaran():
            row = ctk.CTkFrame(card.body, fg_color=theme.SURFACE_LOW, corner_radius=6)
            row.pack(fill="x", padx=18, pady=4)
            ctk.CTkLabel(row, text=ta["nama"], anchor="w", font=(theme.FONT, 13, "bold"), text_color=theme.TEXT).pack(
                side="left", fill="x", expand=True, padx=12, pady=10
            )
            if ta["is_aktif"]:
                badge(row, "aktif", "aktif").pack(side="right", padx=10)
            else:
                danger_button(row, "Hapus", command=lambda ta_id=ta["id"]: self._delete_ta(ta_id), width=72).pack(side="right", padx=8, pady=7)
                secondary_button(row, "Aktifkan", command=lambda ta_id=ta["id"]: self._activate_ta(ta_id), width=90).pack(
                    side="right", padx=8, pady=7
                )
            secondary_button(row, "Edit", command=lambda ta_id=ta["id"], nama=ta["nama"]: self._edit_ta(ta_id, nama), width=70).pack(side="right", padx=8, pady=7)
            for sem in self.repo.list_semester(ta["id"]):
                sem_row = ctk.CTkFrame(card.body, fg_color=theme.SURFACE, corner_radius=6)
                sem_row.pack(fill="x", padx=32, pady=2)
                ctk.CTkLabel(sem_row, text=f"{sem['nama']}", anchor="w", text_color=theme.TEXT_MUTED).pack(
                    side="left", fill="x", expand=True, padx=12, pady=8
                )
                if sem["is_aktif"]:
                    badge(sem_row, "aktif", "aktif").pack(side="right", padx=10)
                else:
                    danger_button(sem_row, "Hapus", command=lambda sem_id=sem["id"]: self._delete_semester(sem_id), width=70).pack(side="right", padx=8, pady=6)
                    secondary_button(sem_row, "Aktifkan", command=lambda sem_id=sem["id"]: self._activate_semester(sem_id), width=90).pack(
                        side="right", padx=8, pady=6
                    )
                secondary_button(sem_row, "Edit", command=lambda sem_id=sem["id"], nama=sem["nama"]: self._edit_semester(sem_id, nama), width=70).pack(side="right", padx=8, pady=6)
        return card

    def _kelas_card(self):
        card = SectionCard(self, "Kelas", "Daftar kelas dipakai sebagai filter siswa, penilaian, dan laporan.")
        nama_var = ctk.StringVar()
        tingkat_var = ctk.StringVar(value="7")
        self.kelas_nama_var = nama_var
        self.kelas_tingkat_var = tingkat_var
        self._labeled_entry(card.body, "Nama Kelas", "Contoh: 7A, 8B, 9C", nama_var)
        self._labeled_option(card.body, "Tingkat", ["7", "8", "9"], tingkat_var)

        def save():
            try:
                nama = nama_var.get().strip().upper()
                tingkat = int(tingkat_var.get())
                if self.editing_kelas_id is None:
                    self.repo.create_kelas(nama, tingkat)
                    show_toast(self, "Kelas ditambahkan", f"{nama} masuk daftar kelas.")
                else:
                    self.repo.update_kelas(self.editing_kelas_id, nama, tingkat)
                    show_toast(self, "Kelas diperbarui", f"{nama} berhasil diedit.", "info")
                self._cancel_edit_kelas(reset_only=True)
                self.refresh_callback()
            except Exception as exc:
                messagebox.showerror("Gagal menyimpan kelas", str(exc))

        self.kelas_save_button = primary_button(card.body, "Tambah Kelas", command=save)
        self.kelas_save_button.pack(fill="x", padx=18, pady=(12, 8))
        self.kelas_cancel_button = secondary_button(card.body, "Batal Edit", command=self._cancel_edit_kelas)
        self.kelas_cancel_button.pack(fill="x", padx=18, pady=(0, 18))
        self.kelas_cancel_button.pack_forget()
        ctk.CTkLabel(
            card.body,
            text="Kelas Tersimpan",
            font=(theme.FONT, 13, "bold"),
            text_color=theme.TEXT_MUTED,
            anchor="w",
        ).pack(fill="x", padx=18, pady=(0, 6))
        for kelas in self.repo.list_kelas():
            row = ctk.CTkFrame(card.body, fg_color=theme.SURFACE_LOW, corner_radius=6)
            row.pack(fill="x", padx=18, pady=4)
            ctk.CTkLabel(row, text=kelas["nama"], anchor="w", font=(theme.FONT, 14, "bold"), text_color=theme.TEXT).pack(
                side="left", fill="x", expand=True, padx=12, pady=10
            )
            badge(row, f"Tingkat {kelas['tingkat']}", "info").pack(side="right", padx=10)
            danger_button(row, "Hapus", command=lambda kelas_id=kelas["id"]: self._delete_kelas(kelas_id), width=72).pack(side="right", padx=8, pady=7)
            secondary_button(row, "Edit", command=lambda data=kelas: self._start_edit_kelas(data), width=70).pack(side="right", padx=8, pady=7)
        return card

    def _labeled_entry(self, parent, label: str, placeholder: str, variable: ctk.StringVar) -> None:
        ctk.CTkLabel(
            parent,
            text=label,
            font=(theme.FONT, 13, "bold"),
            text_color=theme.TEXT,
            anchor="w",
        ).pack(fill="x", padx=18, pady=(8, 4))
        styled_entry(parent, variable, placeholder).pack(fill="x", padx=18, pady=(0, 8))

    def _labeled_option(self, parent, label: str, values: list[str], variable: ctk.StringVar) -> None:
        ctk.CTkLabel(
            parent,
            text=label,
            font=(theme.FONT, 13, "bold"),
            text_color=theme.TEXT,
            anchor="w",
        ).pack(fill="x", padx=18, pady=(8, 4))
        styled_option(parent, values, variable).pack(fill="x", padx=18, pady=(0, 8))

    def _activate_ta(self, tahun_ajaran_id: int):
        self.repo.set_tahun_ajaran_aktif(tahun_ajaran_id)
        show_toast(self, "Tahun ajaran diaktifkan", "Periode aktif berhasil diperbarui.")
        self.refresh_callback()

    def _activate_semester(self, semester_id: int):
        self.repo.set_semester_aktif(semester_id)
        show_toast(self, "Semester diaktifkan", "Semester aktif berhasil diperbarui.")
        self.refresh_callback()

    def _edit_ta(self, tahun_ajaran_id: int, current_name: str):
        dialog = ctk.CTkInputDialog(text="Nama tahun ajaran:", title="Edit Tahun Ajaran")
        value = dialog.get_input()
        if not value:
            return
        self.repo.update_tahun_ajaran(tahun_ajaran_id, value.strip())
        show_toast(self, "Tahun ajaran diperbarui", value.strip(), "info")
        self.refresh_callback()

    def _delete_ta(self, tahun_ajaran_id: int):
        if not messagebox.askyesno("Hapus tahun ajaran", "Tahun ajaran dan semua semester/data terkait akan dihapus permanen. Lanjutkan?"):
            return
        try:
            self.repo.delete_tahun_ajaran(tahun_ajaran_id)
            show_toast(self, "Tahun ajaran dihapus", "Data terkait ikut terhapus.", "warning")
            self.refresh_callback()
        except Exception as exc:
            messagebox.showerror("Gagal menghapus tahun ajaran", str(exc))

    def _edit_semester(self, semester_id: int, current_name: str):
        dialog = ctk.CTkInputDialog(text="Nama semester:", title="Edit Semester")
        value = dialog.get_input()
        if not value:
            return
        self.repo.update_semester(semester_id, value.strip())
        show_toast(self, "Semester diperbarui", value.strip(), "info")
        self.refresh_callback()

    def _delete_semester(self, semester_id: int):
        if not messagebox.askyesno("Hapus semester", "Semester dan semua siswa/materi/nilai terkait akan dihapus permanen. Lanjutkan?"):
            return
        try:
            self.repo.delete_semester(semester_id)
            show_toast(self, "Semester dihapus", "Data terkait ikut terhapus.", "warning")
            self.refresh_callback()
        except Exception as exc:
            messagebox.showerror("Gagal menghapus semester", str(exc))

    def _start_edit_kelas(self, data: dict):
        self.editing_kelas_id = data["id"]
        self.kelas_nama_var.set(data["nama"])
        self.kelas_tingkat_var.set(str(data["tingkat"]))
        self.kelas_save_button.configure(text="Simpan Edit Kelas")
        self.kelas_cancel_button.pack(fill="x", padx=18, pady=(0, 18))
        show_toast(self, "Mode edit kelas", f"Ubah data {data['nama']} lalu simpan.", "info")

    def _cancel_edit_kelas(self, reset_only: bool = False):
        self.editing_kelas_id = None
        self.kelas_nama_var.set("")
        self.kelas_tingkat_var.set("7")
        self.kelas_save_button.configure(text="Tambah Kelas")
        self.kelas_cancel_button.pack_forget()
        if not reset_only:
            show_toast(self, "Edit kelas dibatalkan", "Form kembali ke mode tambah.", "info")

    def _delete_kelas(self, kelas_id: int):
        if not messagebox.askyesno("Hapus kelas", "Kelas hanya bisa dihapus jika belum memiliki siswa. Lanjutkan?"):
            return
        try:
            self.repo.delete_kelas(kelas_id)
            show_toast(self, "Kelas dihapus", "Kelas berhasil dihapus.", "warning")
            self.refresh_callback()
        except Exception as exc:
            messagebox.showerror("Gagal menghapus kelas", str(exc))
