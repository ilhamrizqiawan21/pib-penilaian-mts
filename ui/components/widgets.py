from __future__ import annotations

import customtkinter as ctk

from ui import theme


def clear_frame(frame: ctk.CTkFrame) -> None:
    for child in frame.winfo_children():
        child.destroy()


def font(size: int, weight: str | None = None):
    return (theme.FONT, size) if weight is None else (theme.FONT, size, weight)


def _accent_text(accent: str) -> str:
    bright_accents = {
        theme.ACCENT_MINT,
        theme.PRIMARY_SOFT,
        theme.PRIMARY_SOFT_2,
        theme.ACCENT_BLUE,
        theme.WARNING_BG,
        theme.ERROR_BG,
        theme.INFO_BG,
        theme.GOLD_BG,
    }
    return theme.TEXT if accent.upper() in {value.upper() for value in bright_accents} else theme.SURFACE


class StatCard(ctk.CTkFrame):
    def __init__(
        self,
        master,
        title: str,
        value: str,
        accent: str = theme.PRIMARY,
        icon: str = "",
        note: str | None = None,
        **kwargs,
    ):
        super().__init__(
            master,
            fg_color=theme.SURFACE,
            border_color=theme.BORDER,
            border_width=1,
            corner_radius=24,
            **kwargs,
        )
        self.grid_columnconfigure(1, weight=1, minsize=116)
        icon = ctk.CTkLabel(
            self,
            text=icon,
            width=48,
            height=48,
            fg_color=accent,
            corner_radius=16,
            font=font(16, "bold"),
            text_color=_accent_text(accent),
        )
        icon.grid(row=0, column=0, rowspan=2, padx=(16, 14), pady=16)
        title_label = ctk.CTkLabel(
            self,
            text=title,
            font=font(11, "bold"),
            text_color=theme.TEXT_MUTED,
            anchor="w",
            wraplength=160,
            justify="left",
        )
        title_label.grid(row=0, column=1, sticky="ew", padx=(0, 14), pady=(15, 0))
        ctk.CTkLabel(
            self,
            text=value,
            font=font(28, "bold"),
            text_color=theme.TEXT,
            anchor="w",
        ).grid(row=1, column=1, sticky="ew", padx=(0, 14), pady=(0, 16))
        if note:
            ctk.CTkLabel(
                self,
                text=note,
                font=font(11, "bold"),
                text_color=theme.PRIMARY,
                fg_color=theme.PRIMARY_SOFT,
                corner_radius=999,
                padx=10,
                height=26,
            ).grid(row=2, column=0, columnspan=2, padx=16, pady=(0, 14), sticky="w")


class SectionCard(ctk.CTkFrame):
    def __init__(self, master, title: str | None = None, subtitle: str | None = None, **kwargs):
        super().__init__(
            master,
            fg_color=theme.SURFACE,
            border_color=theme.BORDER,
            border_width=1,
            corner_radius=20,
            **kwargs,
        )
        if title or subtitle:
            header = ctk.CTkFrame(self, fg_color=theme.SURFACE, corner_radius=20)
            header.pack(fill="x", padx=20, pady=(18, 10))
            if title:
                ctk.CTkLabel(
                    header,
                    text=title,
                    font=font(18, "bold"),
                    text_color=theme.TEXT,
                    anchor="w",
                ).pack(anchor="w")
            if subtitle:
                ctk.CTkLabel(
                    header,
                    text=subtitle,
                    font=font(13),
                    text_color=theme.TEXT_MUTED,
                    anchor="w",
                    wraplength=760,
                    justify="left",
                ).pack(anchor="w", pady=(3, 0))
        self.body = ctk.CTkFrame(self, fg_color=theme.SURFACE, corner_radius=20)
        self.body.pack(fill="both", expand=True, padx=0, pady=(0, 14))


class PageHero(ctk.CTkFrame):
    def __init__(
        self,
        master,
        eyebrow: str,
        title: str,
        subtitle: str,
        trailing_text: str | None = None,
        trailing_status: str = "info",
        **kwargs,
    ):
        super().__init__(
            master,
            fg_color=theme.SURFACE_ACCENT,
            border_color=theme.BORDER,
            border_width=1,
            corner_radius=24,
            **kwargs,
        )
        self.grid_columnconfigure(0, weight=1)
        copy = ctk.CTkFrame(self, fg_color=theme.SURFACE_ACCENT, corner_radius=24)
        copy.grid(row=0, column=0, sticky="ew", padx=22, pady=20)
        ctk.CTkLabel(
            copy,
            text=eyebrow.upper(),
            font=font(11, "bold"),
            text_color=theme.PRIMARY,
            anchor="w",
        ).pack(anchor="w")
        ctk.CTkLabel(
            copy,
            text=title,
            font=font(30, "bold"),
            text_color=theme.TEXT,
            anchor="w",
        ).pack(anchor="w", pady=(3, 2))
        ctk.CTkLabel(
            copy,
            text=subtitle,
            font=font(14),
            text_color=theme.TEXT_MUTED,
            anchor="w",
            wraplength=780,
            justify="left",
        ).pack(anchor="w")
        if trailing_text:
            badge(self, trailing_text, trailing_status).grid(row=0, column=1, sticky="e", padx=22, pady=22)


class ModernPanel(ctk.CTkFrame):
    def __init__(self, master, title: str, subtitle: str | None = None, **kwargs):
        super().__init__(
            master,
            fg_color=theme.SURFACE,
            border_color=theme.BORDER,
            border_width=1,
            corner_radius=24,
            **kwargs,
        )
        self.grid_columnconfigure(0, weight=1)
        header = ctk.CTkFrame(self, fg_color=theme.SURFACE, corner_radius=24)
        header.grid(row=0, column=0, sticky="ew", padx=20, pady=(18, 8))
        header.grid_columnconfigure(0, weight=1)
        ctk.CTkLabel(header, text=title, font=font(20, "bold"), text_color=theme.TEXT, anchor="w").grid(
            row=0, column=0, sticky="ew"
        )
        if subtitle:
            ctk.CTkLabel(
                header,
                text=subtitle,
                font=font(13),
                text_color=theme.TEXT_MUTED,
                anchor="w",
                wraplength=760,
                justify="left",
            ).grid(row=1, column=0, sticky="ew", pady=(3, 0))
        self.body = ctk.CTkFrame(self, fg_color=theme.SURFACE, corner_radius=24)
        self.body.grid(row=1, column=0, sticky="nsew", padx=0, pady=(0, 16))


class ActionBar(ctk.CTkFrame):
    def __init__(self, master, **kwargs):
        super().__init__(
            master,
            fg_color=theme.SURFACE,
            border_color=theme.BORDER,
            border_width=1,
            corner_radius=theme.RADIUS,
            **kwargs,
        )


def primary_button(master, text: str, command=None, width: int | None = None):
    kwargs = {"width": width} if width is not None else {}
    return ctk.CTkButton(
        master,
        text=text,
        command=command,
        height=52,
        fg_color=theme.ACCENT_MINT,
        hover_color=theme.PRIMARY_SOFT_2,
        text_color=theme.TEXT,
        corner_radius=999,
        font=font(13, "bold"),
        **kwargs,
    )


def secondary_button(master, text: str, command=None, width: int | None = None, state: str = "normal"):
    kwargs = {"width": width} if width is not None else {}
    return ctk.CTkButton(
        master,
        text=text,
        command=command,
        height=48,
        fg_color=theme.PRIMARY_SOFT,
        hover_color=theme.PRIMARY_SOFT_2,
        text_color=theme.TEXT,
        border_color=theme.BORDER,
        border_width=1,
        corner_radius=999,
        font=font(13, "bold"),
        state=state,
        **kwargs,
    )


def danger_button(master, text: str, command=None, width: int | None = None):
    kwargs = {"width": width} if width is not None else {}
    return ctk.CTkButton(
        master,
        text=text,
        command=command,
        height=48,
        fg_color=theme.ERROR_BG,
        hover_color="#FFC8C1",
        text_color=theme.ERROR_TEXT,
        border_color="#F3B6AF",
        border_width=1,
        corner_radius=999,
        font=font(13, "bold"),
        **kwargs,
    )


def icon_button(master, text: str, command=None, width: int = 42, state: str = "normal"):
    return ctk.CTkButton(
        master,
        text=text,
        command=command,
        width=width,
        height=48,
        fg_color=theme.PRIMARY_SOFT,
        hover_color=theme.PRIMARY_SOFT,
        text_color=theme.PRIMARY,
        border_color=theme.BORDER,
        border_width=1,
        corner_radius=999,
        font=font(16, "bold"),
        state=state,
    )


def styled_entry(master, variable=None, placeholder: str = "", width: int | None = None):
    kwargs = {"width": width} if width is not None else {}
    return ctk.CTkEntry(
        master,
        textvariable=variable,
        placeholder_text=placeholder,
        height=48,
        fg_color=theme.SURFACE_RAISED,
        border_color=theme.BORDER,
        text_color=theme.TEXT,
        placeholder_text_color=theme.TEXT_SUBTLE,
        corner_radius=16,
        font=font(13),
        **kwargs,
    )


def styled_option(master, values: list[str], variable, command=None, width: int | None = None):
    kwargs = {"width": width} if width is not None else {}
    return ctk.CTkOptionMenu(
        master,
        values=values,
        variable=variable,
        command=command,
        height=48,
        fg_color=theme.SURFACE_RAISED,
        button_color=theme.ACCENT_MINT,
        button_hover_color=theme.PRIMARY_SOFT_2,
        text_color=theme.TEXT,
        dropdown_fg_color=theme.SURFACE,
        dropdown_hover_color=theme.PRIMARY_SOFT,
        dropdown_text_color=theme.TEXT,
        corner_radius=16,
        font=font(13, "bold"),
        dropdown_font=font(13),
        anchor="w",
        **kwargs,
    )


class TableHeader(ctk.CTkFrame):
    def __init__(self, master, columns: list[tuple[str, int | None]], **kwargs):
        super().__init__(master, fg_color=theme.TABLE_HEADER, corner_radius=16, **kwargs)
        for text, width in columns:
            label_kwargs = {} if width is None else {"width": width}
            ctk.CTkLabel(
                self,
                text=text.upper(),
                anchor="w",
                font=font(11, "bold"),
                text_color=theme.TEXT_MUTED,
                **label_kwargs,
            ).pack(side="left", fill="x", expand=width is None, padx=12, pady=12)


class TableRow(ctk.CTkFrame):
    def __init__(self, master, index: int = 0, **kwargs):
        super().__init__(
            master,
            fg_color=theme.TABLE_ROW_ALT if index % 2 else theme.SURFACE,
            border_color=theme.BORDER,
            border_width=1,
            corner_radius=16,
            **kwargs,
        )


class ToastNotification(ctk.CTkFrame):
    def __init__(self, master, title: str, message: str = "", status: str = "success", duration_ms: int = 2600):
        colors = {
            "success": (theme.SUCCESS_BG, theme.SUCCESS_TEXT, "OK"),
            "info": (theme.INFO_BG, theme.INFO_TEXT, "IN"),
            "warning": (theme.WARNING_BG, theme.WARNING_TEXT, "!"),
            "error": (theme.ERROR_BG, theme.ERROR_TEXT, "ER"),
        }
        bg, fg, icon = colors.get(status, colors["info"])
        super().__init__(
            master,
            fg_color=theme.SURFACE,
            border_color=theme.BORDER,
            border_width=1,
            corner_radius=theme.RADIUS_LG,
        )
        self.duration_ms = duration_ms
        self.target_y = 18
        self.current_y = -90
        self.configure(width=360, height=82)
        self.pack_propagate(False)

        ctk.CTkLabel(
            self,
            text=icon,
            width=42,
            height=42,
            fg_color=bg,
            text_color=fg,
            corner_radius=999,
            font=font(12, "bold"),
        ).pack(side="left", padx=(14, 12), pady=18)
        text_box = ctk.CTkFrame(self, fg_color=theme.SURFACE)
        text_box.pack(side="left", fill="both", expand=True, pady=14)
        ctk.CTkLabel(text_box, text=title, font=font(13, "bold"), text_color=theme.TEXT, anchor="w").pack(fill="x")
        if message:
            ctk.CTkLabel(
                text_box,
                text=message,
                font=font(12),
                text_color=theme.TEXT_MUTED,
                anchor="w",
                wraplength=250,
                justify="left",
            ).pack(fill="x", pady=(3, 0))
        ctk.CTkButton(
            self,
            text="x",
            width=28,
            height=28,
            fg_color=theme.SURFACE_LOW,
            hover_color=theme.TABLE_HEADER,
            text_color=theme.TEXT_MUTED,
            corner_radius=999,
            command=self.dismiss,
        ).pack(side="right", padx=(4, 12), pady=20)

    def show(self) -> None:
        self.place(relx=1, x=-22, y=self.current_y, anchor="ne")
        self.lift()
        self._slide_in()

    def _slide_in(self) -> None:
        if self.current_y >= self.target_y:
            self.current_y = self.target_y
            self.place_configure(y=self.current_y)
            self.after(self.duration_ms, self.dismiss)
            return
        self.current_y += max(4, int((self.target_y - self.current_y) * 0.35))
        self.place_configure(y=self.current_y)
        self.after(12, self._slide_in)

    def dismiss(self) -> None:
        self._slide_out()

    def _slide_out(self) -> None:
        if self.current_y <= -90:
            self.destroy()
            return
        self.current_y -= 10
        self.place_configure(y=self.current_y)
        self.after(12, self._slide_out)


class LoadingOverlay(ctk.CTkFrame):
    def __init__(self, master, title: str = "Memproses", message: str = "Mohon tunggu sebentar..."):
        super().__init__(master, fg_color=theme.OVERLAY_BG, corner_radius=theme.RADIUS_LG)
        self.configure(border_color=theme.BORDER, border_width=1)
        self.place(relx=0.5, rely=0.5, anchor="center")
        self.lift()
        box = ctk.CTkFrame(self, fg_color=theme.SURFACE, border_color=theme.BORDER, border_width=1, corner_radius=theme.RADIUS_LG)
        box.pack(padx=18, pady=18)
        ctk.CTkLabel(
            box,
            text=title,
            font=font(15, "bold"),
            text_color=theme.TEXT,
        ).pack(padx=24, pady=(18, 4))
        ctk.CTkLabel(
            box,
            text=message,
            font=font(12),
            text_color=theme.TEXT_MUTED,
            wraplength=260,
            justify="center",
        ).pack(padx=24, pady=(0, 12))
        self.progress = ctk.CTkProgressBar(box, width=260, mode="indeterminate", progress_color=theme.PRIMARY)
        self.progress.pack(padx=24, pady=(0, 18))
        self.progress.start()

    def close(self) -> None:
        try:
            self.progress.stop()
        except Exception:
            pass
        self.destroy()


def show_toast(master, title: str, message: str = "", status: str = "success") -> None:
    root = master.winfo_toplevel()
    existing = getattr(root, "_active_toast", None)
    if existing is not None and existing.winfo_exists():
        existing.destroy()
    toast = ToastNotification(root, title, message, status=status)
    root._active_toast = toast
    toast.show()


def show_loading(master, title: str = "Memproses", message: str = "Mohon tunggu sebentar...") -> LoadingOverlay:
    root = master.winfo_toplevel()
    overlay = LoadingOverlay(root, title, message)
    root.update_idletasks()
    return overlay


class EmptyState(ctk.CTkFrame):
    def __init__(self, master, title: str, message: str, **kwargs):
        super().__init__(
            master,
            fg_color=theme.SURFACE,
            border_color=theme.BORDER,
            border_width=1,
            corner_radius=theme.RADIUS_LG,
            **kwargs,
        )
        ctk.CTkLabel(
            self,
            text="PIB",
            width=56,
            height=56,
            fg_color=theme.PRIMARY_SOFT,
            text_color=theme.PRIMARY,
            corner_radius=999,
            font=font(16, "bold"),
        ).pack(pady=(28, 8))
        ctk.CTkLabel(self, text=title, font=font(18, "bold"), text_color=theme.TEXT).pack(pady=(0, 6))
        ctk.CTkLabel(
            self,
            text=message,
            font=font(13),
            text_color=theme.TEXT_MUTED,
            wraplength=520,
            justify="center",
        ).pack(padx=30, pady=(0, 28))


def badge(master, text: str, status: str):
    colors = {
        "lengkap": (theme.SUCCESS_BG, theme.SUCCESS_TEXT),
        "sebagian": (theme.WARNING_BG, theme.WARNING_TEXT),
        "belum": (theme.ERROR_BG, theme.ERROR_TEXT),
        "aktif": (theme.SUCCESS_BG, theme.SUCCESS_TEXT),
        "nonaktif": (theme.ERROR_BG, theme.ERROR_TEXT),
        "info": (theme.INFO_BG, theme.INFO_TEXT),
        "gold": (theme.GOLD_BG, theme.GOLD_TEXT),
    }
    bg, fg = colors.get(status, (theme.SURFACE_LOW, theme.TEXT_MUTED))
    return ctk.CTkLabel(
        master,
        text=text.upper(),
        fg_color=bg,
        text_color=fg,
        corner_radius=999,
        padx=12,
        height=30,
        font=font(11, "bold"),
    )


StatusBadge = badge
