from __future__ import annotations

from tkinter import messagebox

import customtkinter as ctk

from ui import theme
from ui.components.widgets import EmptyState, SectionCard, TableRow, badge, danger_button, primary_button, secondary_button, show_toast, styled_entry


class MateriView(ctk.CTkFrame):
    def __init__(self, master, repo, refresh_callback):
        super().__init__(master, fg_color=theme.BACKGROUND)
        self.repo = repo
        self.refresh_callback = refresh_callback
        self.semester = repo.get_semester_aktif()
        self.editing_materi_name: str | None = None
        self.grid_columnconfigure(0, weight=1)

        hero = ctk.CTkFrame(self, fg_color=theme.SURFACE_ACCENT, border_color=theme.BORDER, border_width=1, corner_radius=12)
        hero.grid(row=0, column=0, sticky="ew", pady=(0, 18))
        hero.grid_columnconfigure(0, weight=1)
        ctk.CTkLabel(hero, text="Materi Penilaian", font=(theme.FONT, 26, "bold"), text_color=theme.TEXT).grid(
            row=0, column=0, sticky="w", padx=20, pady=(18, 4)
        )
        ctk.CTkLabel(
            hero,
            text="Materi dinamis per semester. Poin pengurangan dipakai untuk menghitung nilai otomatis.",
            font=(theme.FONT, 14),
            text_color=theme.TEXT_MUTED,
        ).grid(row=1, column=0, sticky="w", padx=20, pady=(0, 18))

        if not self.semester:
            EmptyState(self, "Belum ada semester aktif", "Buat periode aktif sebelum menambah materi.").grid(row=1, column=0, sticky="ew")
            return

        self._form().grid(row=1, column=0, sticky="ew", pady=(0, 18))
        self._table().grid(row=2, column=0, sticky="ew")

    def _form(self):
        card = SectionCard(self, "Tambah Materi", "Satu nama materi otomatis memiliki aspek Hafalan dan Praktik.")
        self.nama_var = ctk.StringVar()
        self.poin_hafalan_var = ctk.StringVar(value="2")
        self.poin_praktik_var = ctk.StringVar(value="3")
        self.urutan_var = ctk.StringVar(value="1")

        form = ctk.CTkFrame(card.body, fg_color=theme.SURFACE)
        form.pack(fill="x", padx=16, pady=(4, 16))
        form.grid_columnconfigure(0, weight=1)

        self._field_label(form, "Nama Materi").grid(row=0, column=0, sticky="w", pady=(0, 4))
        self._field_label(form, "Poin Hafalan").grid(row=0, column=1, sticky="w", padx=(12, 0), pady=(0, 4))
        self._field_label(form, "Poin Praktik").grid(row=0, column=2, sticky="w", padx=(12, 0), pady=(0, 4))
        self._field_label(form, "Urutan").grid(row=0, column=3, sticky="w", padx=(12, 0), pady=(0, 4))

        styled_entry(form, self.nama_var, "Contoh: Surat Al-Fatihah").grid(row=1, column=0, sticky="ew")
        styled_entry(form, self.poin_hafalan_var, "2", width=140).grid(row=1, column=1, sticky="ew", padx=(12, 0))
        styled_entry(form, self.poin_praktik_var, "3", width=140).grid(row=1, column=2, sticky="ew", padx=(12, 0))
        styled_entry(form, self.urutan_var, "1", width=90).grid(row=1, column=3, sticky="ew", padx=(12, 0))
        self.save_button = primary_button(form, "Tambah Materi", command=self._save, width=130)
        self.save_button.grid(row=1, column=4, padx=(12, 0))
        self.cancel_edit_button = secondary_button(form, "Batal", command=self._cancel_edit, width=80)
        self.cancel_edit_button.grid(row=1, column=5, padx=(8, 0))
        self.cancel_edit_button.grid_remove()
        return card

    def _table(self):
        card = SectionCard(self, "Daftar Materi Aktif", "Materi aktif akan muncul di pilihan Nama Materi pada menu Penilaian.")
        wrapper = ctk.CTkFrame(card.body, fg_color=theme.SURFACE)
        wrapper.pack(fill="x", padx=14)
        names = self.repo.list_nama_materi(self.semester["id"])
        if not names:
            ctk.CTkLabel(wrapper, text="Belum ada materi. Tambahkan lewat form di atas.", text_color=theme.TEXT_MUTED).pack(anchor="w", padx=14, pady=14)
            return card
        for idx, name in enumerate(names, start=1):
            pair = self.repo.ensure_materi_pair_by_nama(self.semester["id"], name)
            row = TableRow(wrapper, idx)
            row.pack(fill="x", padx=4, pady=4)
            ctk.CTkLabel(row, text=f"{idx}. {name}", anchor="w", font=(theme.FONT, 13, "bold")).pack(side="left", fill="x", expand=True, padx=12, pady=10)
            badge(row, f"Hafalan -{pair['hafalan']['poin_pengurangan']}", "info").pack(side="left", padx=6)
            badge(row, f"Praktik -{pair['praktik']['poin_pengurangan']}", "info").pack(side="left", padx=6)
            secondary_button(row, "Edit", command=lambda materi_name=name: self._start_edit(materi_name), width=72).pack(side="right", padx=(4, 8), pady=8)
            danger_button(row, "Hapus", command=lambda materi_name=name: self._delete_pair(materi_name), width=76).pack(side="right", padx=(8, 4), pady=8)
        return card

    def _field_label(self, parent, text: str):
        return ctk.CTkLabel(
            parent,
            text=text,
            font=(theme.FONT, 13, "bold"),
            text_color=theme.TEXT,
            anchor="w",
        )

    def _save(self):
        try:
            data = {
                "semester_id": self.semester["id"],
                "nama": self.nama_var.get().strip(),
                "poin_hafalan": float(self.poin_hafalan_var.get()),
                "poin_praktik": float(self.poin_praktik_var.get()),
                "urutan": int(self.urutan_var.get() or 0),
            }
            if self.editing_materi_name is None:
                self.repo.create_materi_pair(data)
                show_toast(self, "Materi disimpan", f"{data['nama']} siap dinilai.")
            else:
                self.repo.update_materi_pair_by_nama(self.semester["id"], self.editing_materi_name, data)
                show_toast(self, "Materi diperbarui", f"{data['nama']} berhasil diedit.", "info")
            self._cancel_edit(reset_only=True)
            self.refresh_callback()
        except Exception as exc:
            messagebox.showerror("Gagal menyimpan materi", str(exc))

    def _start_edit(self, name: str):
        pair = self.repo.ensure_materi_pair_by_nama(self.semester["id"], name)
        self.editing_materi_name = name
        self.nama_var.set(name)
        self.poin_hafalan_var.set(str(pair["hafalan"]["poin_pengurangan"]))
        self.poin_praktik_var.set(str(pair["praktik"]["poin_pengurangan"]))
        self.urutan_var.set(str(pair["hafalan"]["urutan"]))
        self.save_button.configure(text="Simpan Edit")
        self.cancel_edit_button.grid()
        show_toast(self, "Mode edit materi", f"Ubah data {name} lalu simpan.", "info")

    def _cancel_edit(self, reset_only: bool = False):
        self.editing_materi_name = None
        self.nama_var.set("")
        self.poin_hafalan_var.set("2")
        self.poin_praktik_var.set("3")
        self.urutan_var.set("1")
        self.save_button.configure(text="Tambah Materi")
        self.cancel_edit_button.grid_remove()
        if not reset_only:
            show_toast(self, "Edit dibatalkan", "Form kembali ke mode tambah.", "info")

    def _deactivate(self, materi_id: int):
        if not messagebox.askyesno("Nonaktifkan materi", "Materi tidak akan muncul di penilaian aktif. Lanjutkan?"):
            return
        self.repo.deactivate_materi(materi_id)
        show_toast(self, "Materi dinonaktifkan", "Materi tidak tampil pada penilaian aktif.", "warning")
        self.refresh_callback()

    def _delete_pair(self, name: str):
        if not messagebox.askyesno("Hapus materi", f"Materi {name} beserta nilai terkait akan dihapus permanen. Lanjutkan?"):
            return
        self.repo.delete_materi_pair_by_nama(self.semester["id"], name)
        show_toast(self, "Materi dihapus", f"{name} dan nilai terkait sudah dihapus.", "warning")
        self.refresh_callback()
