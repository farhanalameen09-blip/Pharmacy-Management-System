"""
Shared UI toolkit for the Pharmacy Management System.

Import from any page:

    from ui_kit import styled_treeview, PageHeader, StatCard, EmptyState, show_toast

`apply_theme()` is called once in main.py. It re-skins every CustomTkinter
widget (buttons, inputs, frames, scrollbars...) with the palette from
config.Colors, so existing pages pick up the new look without code changes.
"""

import customtkinter as ctk # type: ignore

from tkinter import ttk

from config import Colors, Fonts, Shape, Spacing


# ============================================================
# GLOBAL THEME
# ============================================================

def apply_theme():
    """Override CustomTkinter's default colors with the app palette."""

    theme = ctk.ThemeManager.theme

    def update(widget, **values):
        if widget in theme:
            theme[widget].update(values)

    update("CTkFrame",
           fg_color=Colors.SURFACE,
           top_fg_color=Colors.SURFACE_ALT,
           border_color=Colors.BORDER,
           corner_radius=Shape.RADIUS_LG)

    update("CTkScrollableFrame",
           label_fg_color=Colors.SURFACE_ALT)

    update("CTkButton",
           fg_color=Colors.PRIMARY,
           hover_color=Colors.PRIMARY_HOVER,
           text_color=Colors.PRIMARY_TEXT,
           border_color=Colors.BORDER,
           corner_radius=Shape.RADIUS_MD)

    update("CTkEntry",
           fg_color=Colors.SURFACE,
           border_color=Colors.BORDER,
           text_color=Colors.TEXT,
           placeholder_text_color=Colors.TEXT_MUTED,
           corner_radius=Shape.RADIUS_SM,
           border_width=1)

    update("CTkTextbox",
           fg_color=Colors.SURFACE,
           border_color=Colors.BORDER,
           text_color=Colors.TEXT,
           corner_radius=Shape.RADIUS_SM,
           border_width=1)

    update("CTkComboBox",
           fg_color=Colors.SURFACE,
           border_color=Colors.BORDER,
           button_color=Colors.PRIMARY,
           button_hover_color=Colors.PRIMARY_HOVER,
           text_color=Colors.TEXT,
           corner_radius=Shape.RADIUS_SM)

    update("CTkOptionMenu",
           fg_color=Colors.PRIMARY,
           button_color=Colors.PRIMARY_HOVER,
           button_hover_color=Colors.PRIMARY_HOVER,
           text_color=Colors.PRIMARY_TEXT,
           corner_radius=Shape.RADIUS_SM)

    update("CTkSegmentedButton",
           fg_color=Colors.SURFACE_ALT,
           selected_color=Colors.PRIMARY,
           selected_hover_color=Colors.PRIMARY_HOVER,
           unselected_color=Colors.SURFACE_ALT,
           unselected_hover_color=Colors.BORDER,
           text_color=Colors.TEXT,
           corner_radius=Shape.RADIUS_SM)

    update("CTkSwitch",
           progress_color=Colors.PRIMARY,
           button_color=Colors.SURFACE,
           button_hover_color=Colors.SURFACE_ALT)

    update("CTkCheckBox",
           fg_color=Colors.PRIMARY,
           hover_color=Colors.PRIMARY_HOVER,
           border_color=Colors.BORDER)

    update("CTkRadioButton",
           fg_color=Colors.PRIMARY,
           hover_color=Colors.PRIMARY_HOVER,
           border_color=Colors.BORDER)

    update("CTkScrollbar",
           button_color=Colors.BORDER,
           button_hover_color=Colors.TEXT_MUTED)

    update("CTkProgressBar",
           progress_color=Colors.PRIMARY,
           fg_color=Colors.SURFACE_ALT)

    update("CTkLabel", text_color=Colors.TEXT)


# ============================================================
# TABLES (ttk.Treeview)
# ============================================================

TREE_STYLE = "Pharma.Treeview"


def _pick(pair):
    """Return the light or dark value of a (light, dark) color pair."""
    dark = ctk.get_appearance_mode() == "Dark"
    return pair[1] if dark else pair[0]


def apply_treeview_theme():
    """Configure the shared table style for the current light/dark mode."""

    style = ttk.Style()
    style.theme_use("clam")

    bg = _pick(Colors.SURFACE)
    fg = _pick(Colors.TEXT)
    head_bg = _pick(Colors.SURFACE_ALT)
    border = _pick(Colors.BORDER)
    accent = _pick(Colors.PRIMARY)

    style.configure(
        TREE_STYLE,
        background=bg,
        fieldbackground=bg,
        foreground=fg,
        rowheight=Shape.TABLE_ROW_HEIGHT,
        borderwidth=0,
        relief="flat",
        font=(Fonts.BODY["family"], 11),
    )
    style.configure(
        f"{TREE_STYLE}.Heading",
        background=head_bg,
        foreground=fg,
        relief="flat",
        borderwidth=0,
        padding=(10, 9),
        font=(Fonts.BODY["family"], 11, "bold"),
    )
    style.map(
        TREE_STYLE,
        background=[("selected", accent)],
        foreground=[("selected", _pick(Colors.PRIMARY_TEXT))],
    )
    style.map(f"{TREE_STYLE}.Heading", background=[("active", head_bg)])

    for orient in ("Vertical", "Horizontal"):
        style.configure(
            f"{orient}.TScrollbar",
            background=border,
            troughcolor=bg,
            bordercolor=bg,
            arrowcolor=fg,
            relief="flat",
        )


def styled_treeview(parent, **kwargs):
    """Drop-in replacement for ttk.Treeview with the app look.

    Also zebra-stripes rows through the "odd" / "even" tags when the caller
    inserts rows with `zebra(tree)` afterwards.
    """

    apply_treeview_theme()
    kwargs.setdefault("style", TREE_STYLE)
    kwargs.setdefault("selectmode", "browse")

    tree = ttk.Treeview(parent, **kwargs)

    # Re-apply when the page is shown, so a theme switch is picked up.
    tree.bind("<Map>", lambda _e: apply_treeview_theme(), add="+")
    return tree


# ============================================================
# COMPONENTS
# ============================================================

class PageHeader(ctk.CTkFrame):
    """Title + subtitle on the left, action buttons on the right.

        header = PageHeader(self, "Customers", "Manage customer records")
        header.pack(fill="x", padx=25, pady=(25, 10))
        header.add_action("Dashboard", back_callback, secondary=True)
    """

    def __init__(self, parent, title, subtitle=""):
        super().__init__(parent, fg_color="transparent")

        text_box = ctk.CTkFrame(self, fg_color="transparent")
        text_box.pack(side="left")

        ctk.CTkLabel(
            text_box, text=title, anchor="w",
            font=ctk.CTkFont(**Fonts.DISPLAY)
        ).pack(anchor="w")

        if subtitle:
            ctk.CTkLabel(
                text_box, text=subtitle, anchor="w",
                font=ctk.CTkFont(**Fonts.BODY),
                text_color=Colors.TEXT_MUTED
            ).pack(anchor="w", pady=(2, 0))

        self.actions = ctk.CTkFrame(self, fg_color="transparent")
        self.actions.pack(side="right")

    def add_action(self, text, command, secondary=False, width=120):
        options = dict(
            text=text, width=width, height=Shape.BUTTON_HEIGHT,
            command=command, font=ctk.CTkFont(**Fonts.BODY),
        )
        if secondary:
            options.update(
                fg_color="transparent", border_width=1,
                text_color=Colors.TEXT, hover_color=Colors.SURFACE_ALT,
            )
        button = ctk.CTkButton(self.actions, **options)
        button.pack(side="right", padx=(Spacing.SM, 0))
        return button


class StatCard(ctk.CTkFrame):
    """Metric card with a colored accent bar.

        StatCard(parent, "💊", "Total medicines", 128, Colors.PRIMARY)
    """

    def __init__(self, parent, icon, title, value, accent=Colors.PRIMARY):
        super().__init__(parent, corner_radius=Shape.RADIUS_LG)

        self.grid_columnconfigure(1, weight=1)

        ctk.CTkFrame(
            self, width=6, corner_radius=3, fg_color=accent
        ).grid(row=0, column=0, sticky="ns", padx=(12, 0), pady=14)

        body = ctk.CTkFrame(self, fg_color="transparent")
        body.grid(row=0, column=1, sticky="nsew", padx=14, pady=14)

        top = ctk.CTkFrame(body, fg_color="transparent")
        top.pack(fill="x")

        ctk.CTkLabel(
            top, text=title, anchor="w",
            font=ctk.CTkFont(**Fonts.SUBHEADING)
        ).pack(side="left")

        ctk.CTkLabel(
            top, text=icon, font=ctk.CTkFont(size=20)
        ).pack(side="right")

        self.value_label = ctk.CTkLabel(
            body, text=str(value), anchor="w",
            font=ctk.CTkFont(**Fonts.METRIC), text_color=accent
        )
        self.value_label.pack(fill="x", pady=(4, 0))

    def set_value(self, value):
        self.value_label.configure(text=str(value))


class EmptyState(ctk.CTkFrame):
    """Friendly placeholder for tables with nothing to show."""

    def __init__(self, parent, icon="📭", title="Nothing here yet", message=""):
        super().__init__(parent, fg_color="transparent")

        ctk.CTkLabel(self, text=icon, font=ctk.CTkFont(size=44)).pack(pady=(50, 8))
        ctk.CTkLabel(
            self, text=title, font=ctk.CTkFont(**Fonts.HEADING)
        ).pack()
        if message:
            ctk.CTkLabel(
                self, text=message, font=ctk.CTkFont(**Fonts.BODY),
                text_color=Colors.TEXT_MUTED
            ).pack(pady=(4, 0))


def show_toast(parent, message, kind="success", duration=2600):
    """Small non-blocking message in the bottom-right corner.

    kind: "success", "error", "warning" or "info".
    Use instead of messagebox for confirmations that need no decision.
    """

    colors = {
        "success": Colors.SUCCESS,
        "error": Colors.DANGER,
        "warning": Colors.WARNING,
        "info": Colors.INFO,
    }
    icons = {"success": "✓", "error": "✕", "warning": "!", "info": "i"}

    toplevel = parent.winfo_toplevel()

    toast = ctk.CTkFrame(
        toplevel, corner_radius=Shape.RADIUS_MD,
        fg_color=Colors.SURFACE, border_width=2,
        border_color=colors.get(kind, Colors.INFO)
    )
    ctk.CTkLabel(
        toast, text=f" {icons.get(kind, 'i')} ",
        font=ctk.CTkFont(size=16, weight="bold"),
        text_color=colors.get(kind, Colors.INFO)
    ).pack(side="left", padx=(10, 0), pady=10)
    ctk.CTkLabel(
        toast, text=message, font=ctk.CTkFont(**Fonts.BODY)
    ).pack(side="left", padx=(4, 14), pady=10)

    toast.place(relx=1.0, rely=1.0, x=-24, y=-24, anchor="se")
    toast.lift()
    toast.after(duration, toast.destroy)
    return toast
