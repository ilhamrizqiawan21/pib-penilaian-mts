from __future__ import annotations

import customtkinter as ctk
from PIL import Image

from config import APP_TITLE, APP_VERSION, LOGO_ICO_PATH, LOGO_PATH
from database.connection import is_db_initialized
from database.repository import Repository
from ui import theme
from ui.components.widgets import clear_frame
from ui.dashboard_view import DashboardView
from ui.laporan_view import LaporanView
from ui.materi_view import MateriView
from ui.penilaian_view import PenilaianView
from ui.periode_view import PeriodeView
from ui.siswa_view import SiswaView
from ui.wizard import FirstRunWizard


class PIBApp(ctk.CTk):
    def __init__(self):
        super().__init__()
        ctk.set_appearance_mode("light")
        ctk.set_default_color_theme("blue")

        self.repo = Repository()
        self.active_view = "Dashboard"
        self.nav_buttons: dict[str, ctk.CTkButton] = {}
        self.nav_indicators: dict[str, ctk.CTkFrame] = {}
        self.logo_image = self._load_logo_image(56)
        self.current_view_widget = None
        self._touch_scroll_start_y = 0
        self._touch_scroll_last_y = 0
        self._touch_scroll_dragging = False

        self.title(APP_TITLE)
        if LOGO_ICO_PATH.exists():
            try:
                self.iconbitmap(LOGO_ICO_PATH)
            except Exception:
                pass

        self.geometry("1200x750")
        self.minsize(980, 620)
        self.configure(fg_color=theme.BACKGROUND)
        self.grid_columnconfigure(1, weight=1)
        self.grid_rowconfigure(1, weight=1)

        self.sidebar = ctk.CTkFrame(self, width=250, fg_color=theme.SURFACE, corner_radius=0)
        self.sidebar.grid(row=0, column=0, rowspan=2, sticky="nsew")
        self.sidebar.grid_propagate(False)

        self.header = ctk.CTkFrame(self, height=66, fg_color=theme.BACKGROUND, corner_radius=0)
        self.header.grid(row=0, column=1, sticky="ew")
        self.header.grid_propagate(False)
        self.header.grid_columnconfigure(2, weight=1)

        self.content = ctk.CTkScrollableFrame(self, fg_color=theme.BACKGROUND, corner_radius=0)
        self.content.grid(row=1, column=1, sticky="nsew")
        self._enable_touch_scrolling()
        self.bind("<Configure>", self._on_resize, add="+")

        self._build_sidebar()
        self._build_header()
        self.show_view("Dashboard")

        if not is_db_initialized():
            self.after(250, lambda: FirstRunWizard(self, self.repo, self.refresh_all))

    def _school_name(self) -> str:
        return self.repo.get_pengaturan("nama_sekolah") or "MTs PIB"

    def _load_logo_image(self, size: int) -> ctk.CTkImage | None:
        if not LOGO_PATH.exists():
            return None
        try:
            image = Image.open(LOGO_PATH)
            return ctk.CTkImage(light_image=image, dark_image=image, size=(size, size))
        except Exception:
            return None

    def _build_sidebar(self) -> None:
        clear_frame(self.sidebar)
        self.nav_buttons = {}
        self.nav_indicators = {}
        sekolah = self._school_name()

        brand = ctk.CTkFrame(self.sidebar, fg_color=theme.SURFACE)
        brand.pack(fill="x", padx=16, pady=(18, 14))
        brand.grid_columnconfigure(1, weight=1)

        if self.logo_image:
            ctk.CTkLabel(brand, text="", image=self.logo_image, width=60, height=60).grid(
                row=0, column=0, rowspan=2, sticky="nw", padx=(0, 12)
            )
        else:
            ctk.CTkLabel(
                brand,
                text="PIB",
                width=56,
                height=56,
                fg_color=theme.PRIMARY,
                text_color=theme.SURFACE,
                corner_radius=14,
                font=(theme.FONT, 18, "bold"),
            ).grid(row=0, column=0, rowspan=2, sticky="nw", padx=(0, 12))

        ctk.CTkLabel(
            brand,
            text=sekolah,
            font=(theme.FONT, 17, "bold"),
            text_color=theme.PRIMARY,
            anchor="w",
            wraplength=150,
            justify="left",
        ).grid(row=0, column=1, sticky="ew")
        ctk.CTkLabel(
            brand,
            text="PENILAIAN PIB",
            font=(theme.FONT, 12, "bold"),
            text_color=theme.TEXT_MUTED,
            anchor="w",
        ).grid(row=1, column=1, sticky="ew", pady=(3, 0))

        ctk.CTkFrame(self.sidebar, height=1, fg_color=theme.DIVIDER).pack(fill="x", padx=18, pady=(0, 14))
        ctk.CTkLabel(
            self.sidebar,
            text="MENU UTAMA",
            font=(theme.FONT, 11, "bold"),
            text_color=theme.TEXT_SUBTLE,
            anchor="w",
        ).pack(fill="x", padx=22, pady=(0, 8))

        menu_frame = ctk.CTkFrame(self.sidebar, fg_color=theme.SURFACE)
        menu_frame.pack(fill="x", padx=10, pady=(0, 0))

        menu_icons = {
            "Dashboard": "DB",
            "Periode": "PR",
            "Siswa": "SW",
            "Materi": "MT",
            "Penilaian": "NL",
            "Laporan": "LP",
        }
        for label in ["Dashboard", "Periode", "Siswa", "Materi", "Penilaian", "Laporan"]:
            row = ctk.CTkFrame(menu_frame, fg_color=theme.SURFACE, corner_radius=theme.RADIUS_LG, height=46)
            row.pack(fill="x", padx=0, pady=4)
            row.pack_propagate(False)
            indicator = ctk.CTkFrame(row, width=4, height=32, fg_color=theme.SURFACE, corner_radius=10)
            indicator.pack(side="left", padx=(0, 5), pady=6)
            btn = ctk.CTkButton(
                row,
                text=f"{menu_icons[label]}  {label}",
                anchor="w",
                height=42,
                corner_radius=8,
                fg_color=theme.SURFACE,
                hover_color=theme.SURFACE_LOW,
                text_color=theme.TEXT_MUTED,
                font=(theme.FONT, 14, "bold"),
                command=lambda name=label: self.show_view(name),
            )
            btn.pack(side="left", fill="x", expand=True, padx=(0, 0), pady=2)
            self.nav_buttons[label] = btn
            self.nav_indicators[label] = indicator

        helper = ctk.CTkFrame(self.sidebar, fg_color=theme.PRIMARY_SOFT, corner_radius=theme.RADIUS_LG)
        helper.pack(side="bottom", fill="x", padx=16, pady=(0, 12))
        ctk.CTkLabel(
            helper,
            text="Mode kerja lokal",
            font=(theme.FONT, 13, "bold"),
            text_color=theme.PRIMARY,
            anchor="w",
        ).pack(fill="x", padx=14, pady=(12, 2))
        ctk.CTkLabel(
            helper,
            text="Data tersimpan offline. Backup file data/pib.db secara berkala.",
            font=(theme.FONT, 11),
            text_color=theme.TEXT_MUTED,
            anchor="w",
            wraplength=200,
            justify="left",
        ).pack(fill="x", padx=14, pady=(0, 12))
        ctk.CTkLabel(
            self.sidebar,
            text=f"v{APP_VERSION}",
            font=(theme.FONT, 11),
            text_color=theme.TEXT_MUTED,
        ).pack(side="bottom", anchor="w", padx=22, pady=(0, 10))

    def _build_header(self) -> None:
        clear_frame(self.header)
        sekolah = self._school_name()
        semester = self.repo.get_semester_aktif()
        periode = "-"
        if semester:
            periode = f"{semester['nama']} {semester['tahun_ajaran']}"

        ctk.CTkLabel(
            self.header,
            text=sekolah,
            font=(theme.FONT, 19, "bold"),
            text_color=theme.TEXT,
        ).grid(row=0, column=0, padx=(28, 18), pady=18, sticky="w")
        ctk.CTkFrame(self.header, width=1, fg_color=theme.BORDER).grid(row=0, column=1, sticky="ns", pady=18)
        ctk.CTkLabel(
            self.header,
            text=f"Periode aktif: {periode}",
            font=(theme.FONT, 13, "bold"),
            text_color=theme.PRIMARY,
            fg_color=theme.PRIMARY_SOFT,
            corner_radius=999,
            padx=14,
            height=32,
        ).grid(row=0, column=2, padx=18, pady=17, sticky="w")
        ctk.CTkLabel(
            self.header,
            text="Offline",
            fg_color=theme.PRIMARY_SOFT,
            text_color=theme.PRIMARY,
            corner_radius=999,
            padx=12,
            height=28,
            font=(theme.FONT, 12, "bold"),
        ).grid(row=0, column=3, padx=28, pady=18, sticky="e")

    def refresh_all(self) -> None:
        self._build_sidebar()
        self._build_header()
        self.show_view(self.active_view)

    def show_view(self, name: str) -> None:
        self.active_view = name
        for label, btn in self.nav_buttons.items():
            active = label == name
            btn.configure(
                fg_color=theme.PRIMARY_SOFT if active else theme.SURFACE,
                text_color=theme.PRIMARY if active else theme.TEXT_MUTED,
                hover_color=theme.PRIMARY_SOFT if active else theme.SURFACE_LOW,
            )
            self.nav_indicators[label].configure(fg_color=theme.PRIMARY if active else theme.SURFACE)

        clear_frame(self.content)
        view_class = {
            "Dashboard": DashboardView,
            "Periode": PeriodeView,
            "Siswa": SiswaView,
            "Materi": MateriView,
            "Penilaian": PenilaianView,
            "Laporan": LaporanView,
        }[name]
        view = view_class(self.content, self.repo, self.refresh_all)
        self.current_view_widget = view
        padx = self._content_padding()
        view.pack(fill="both", expand=True, padx=padx, pady=24)
        self._bind_touch_scroll_recursive(view)
        self.after(10, self._scroll_content_to_top)

    def _content_padding(self) -> int:
        width = self.winfo_width()
        if width and width < 1100:
            return 18
        if width and width > 1500:
            return 34
        return 26

    def _on_resize(self, event) -> None:
        if event.widget is not self or self.current_view_widget is None:
            return
        try:
            self.current_view_widget.pack_configure(padx=self._content_padding())
        except Exception:
            pass

    def _scroll_content_to_top(self) -> None:
        canvas = getattr(self.content, "_parent_canvas", None)
        if canvas is not None:
            canvas.yview_moveto(0)

    def _enable_touch_scrolling(self) -> None:
        canvas = getattr(self.content, "_parent_canvas", None)
        if canvas is None:
            return
        canvas.bind("<ButtonPress-1>", self._touch_scroll_press, add="+")
        canvas.bind("<B1-Motion>", self._touch_scroll_motion, add="+")
        canvas.bind("<ButtonRelease-1>", self._touch_scroll_release, add="+")
        self.content.bind("<ButtonPress-1>", self._touch_scroll_press, add="+")
        self.content.bind("<B1-Motion>", self._touch_scroll_motion, add="+")
        self.content.bind("<ButtonRelease-1>", self._touch_scroll_release, add="+")

    def _touch_scroll_press(self, event) -> None:
        self._touch_scroll_start_y = event.y_root
        self._touch_scroll_last_y = event.y_root
        self._touch_scroll_dragging = False

    def _touch_scroll_motion(self, event) -> str | None:
        canvas = getattr(self.content, "_parent_canvas", None)
        if canvas is None:
            return None
        delta = event.y_root - self._touch_scroll_last_y
        total_delta = event.y_root - self._touch_scroll_start_y
        if abs(total_delta) < 8:
            return None
        self._touch_scroll_dragging = True
        canvas.yview_scroll(int(-delta), "units")
        self._touch_scroll_last_y = event.y_root
        return "break"

    def _touch_scroll_release(self, event) -> str | None:
        if self._touch_scroll_dragging:
            self._touch_scroll_dragging = False
            return "break"
        return None

    def _bind_touch_scroll_recursive(self, widget) -> None:
        widget_class = widget.winfo_class()
        blocked_classes = {"Entry", "Text", "Spinbox", "TCombobox"}
        if widget_class in blocked_classes or widget.__class__.__name__.lower().startswith("sheet"):
            return
        try:
            widget.bind("<ButtonPress-1>", self._touch_scroll_press, add="+")
            widget.bind("<B1-Motion>", self._touch_scroll_motion, add="+")
            widget.bind("<ButtonRelease-1>", self._touch_scroll_release, add="+")
        except Exception:
            return
        for child in widget.winfo_children():
            self._bind_touch_scroll_recursive(child)
