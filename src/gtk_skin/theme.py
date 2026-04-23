"""GTK-flavored color palettes and ttk style configuration."""

from __future__ import annotations

from dataclasses import dataclass, replace
from tkinter import font as tkfont
from tkinter import ttk
from typing import Literal

StyleName = Literal["gtk3", "gtk4"]


@dataclass(frozen=True)
class Palette:
    """A single GTK color palette.

    Fields map to semantic CSS-like roles used across widgets.
    """

    name: str
    style: StyleName
    dark: bool

    window_bg: str
    view_bg: str
    headerbar_bg: str
    headerbar_fg: str
    headerbar_border: str

    fg: str
    muted_fg: str
    dim_fg: str

    border: str
    strong_border: str

    button_bg: str
    button_bg_hover: str
    button_bg_active: str
    button_border: str

    accent: str
    accent_hover: str
    accent_active: str
    accent_fg: str

    selection_bg: str
    selection_fg: str

    success: str
    warning: str
    error: str

    shadow: str
    # Corner radius in px — GTK4 is noticeably rounder than GTK3.
    radius: int
    # Header bar height in px.
    header_height: int


# --- GTK3 Adwaita ------------------------------------------------------------
# Colors sampled from the adwaita-icon-theme / gtk3 default stylesheet.
GTK3_LIGHT = Palette(
    name="Adwaita",
    style="gtk3",
    dark=False,
    window_bg="#f6f5f4",
    view_bg="#ffffff",
    headerbar_bg="#ebebeb",
    headerbar_fg="#2e3436",
    headerbar_border="#c0bfbc",
    fg="#2e3436",
    muted_fg="#555a5e",
    dim_fg="#929595",
    border="#cdc7c2",
    strong_border="#b6b2ae",
    button_bg="#f6f5f4",
    button_bg_hover="#f9f9f8",
    button_bg_active="#d5d0cc",
    button_border="#cdc7c2",
    accent="#3584e4",
    accent_hover="#5294e8",
    accent_active="#1c71d8",
    accent_fg="#ffffff",
    selection_bg="#3584e4",
    selection_fg="#ffffff",
    success="#26a269",
    warning="#cd9309",
    error="#c01c28",
    shadow="#d8d4d0",
    radius=3,
    header_height=46,
)

GTK3_DARK = replace(
    GTK3_LIGHT,
    name="Adwaita Dark",
    dark=True,
    window_bg="#353535",
    view_bg="#2d2d2d",
    headerbar_bg="#1f1f1f",
    headerbar_fg="#eeeeec",
    headerbar_border="#101010",
    fg="#eeeeec",
    muted_fg="#c0bfbc",
    dim_fg="#888a85",
    border="#1b1b1b",
    strong_border="#0e0e0e",
    button_bg="#4a4a4a",
    button_bg_hover="#555555",
    button_bg_active="#2a2a2a",
    button_border="#1b1b1b",
    accent="#3584e4",
    accent_hover="#5294e8",
    accent_active="#1c71d8",
    shadow="#1b1b1b",
)


# --- GTK4 libadwaita ---------------------------------------------------------
# Flatter, rounder, softer borders. Headerbar blends into the window.
GTK4_LIGHT = Palette(
    name="libadwaita",
    style="gtk4",
    dark=False,
    window_bg="#fafafa",
    view_bg="#ffffff",
    headerbar_bg="#ebebeb",
    headerbar_fg="#1d1d1d",
    headerbar_border="#d9d9d9",
    fg="#1d1d1d",
    muted_fg="#5e5c64",
    dim_fg="#9a9996",
    border="#d9d9d9",
    strong_border="#c0bfbc",
    button_bg="#e8e8e7",
    button_bg_hover="#dededd",
    button_bg_active="#cecdcc",
    button_border="#d9d9d9",
    accent="#3584e4",
    accent_hover="#5294e8",
    accent_active="#1c71d8",
    accent_fg="#ffffff",
    selection_bg="#3584e4",
    selection_fg="#ffffff",
    success="#2ec27e",
    warning="#e5a50a",
    error="#e01b24",
    shadow="#e0e0e0",
    radius=9,
    header_height=48,
)

GTK4_DARK = replace(
    GTK4_LIGHT,
    name="libadwaita Dark",
    dark=True,
    window_bg="#242424",
    view_bg="#1e1e1e",
    headerbar_bg="#303030",
    headerbar_fg="#ffffff",
    headerbar_border="#1b1b1b",
    fg="#ffffff",
    muted_fg="#c0bfbc",
    dim_fg="#77767b",
    border="#404040",
    strong_border="#545454",
    button_bg="#3a3a3a",
    button_bg_hover="#454545",
    button_bg_active="#2a2a2a",
    button_border="#1b1b1b",
    accent="#78aeed",
    accent_hover="#8fbdf0",
    accent_active="#5b9ce6",
    shadow="#1a1a1a",
)


PALETTES: dict[tuple[StyleName, bool], Palette] = {
    ("gtk3", False): GTK3_LIGHT,
    ("gtk3", True): GTK3_DARK,
    ("gtk4", False): GTK4_LIGHT,
    ("gtk4", True): GTK4_DARK,
}


def resolve_palette(style: StyleName = "gtk4", dark: bool = False) -> Palette:
    return PALETTES[(style, dark)]


def _pick_font(root) -> tuple[str, int]:
    """Pick the nicest available GTK-ish font on the current system."""
    preferred = ("Cantarell", "Inter", "Adwaita Sans", "SF Pro Text",
                 "Helvetica Neue", "Segoe UI Variable", "Segoe UI", "Noto Sans")
    available = set(tkfont.families(root))
    for name in preferred:
        if name in available:
            return name, 11
    return "TkDefaultFont", 11


def apply_skin(root, style: StyleName = "gtk4", dark: bool = False) -> Palette:
    """Apply the GTK skin to a Tk root/Toplevel and its ttk widgets.

    Returns the active palette so callers can reuse colors for custom widgets.
    """
    pal = resolve_palette(style, dark)

    family, size = _pick_font(root)
    root.option_add("*Font", (family, size))
    root.option_add("*Background", pal.window_bg)
    root.option_add("*Foreground", pal.fg)
    root.option_add("*selectBackground", pal.selection_bg)
    root.option_add("*selectForeground", pal.selection_fg)
    root.option_add("*Entry.background", pal.view_bg)
    root.option_add("*Entry.foreground", pal.fg)
    root.option_add("*Entry.insertBackground", pal.fg)
    root.option_add("*Text.background", pal.view_bg)
    root.option_add("*Text.foreground", pal.fg)
    root.option_add("*Text.insertBackground", pal.fg)
    root.option_add("*Listbox.background", pal.view_bg)
    root.option_add("*Listbox.foreground", pal.fg)
    root.option_add("*Listbox.selectBackground", pal.selection_bg)
    root.option_add("*Listbox.selectForeground", pal.selection_fg)
    root.option_add("*Menu.background", pal.headerbar_bg)
    root.option_add("*Menu.foreground", pal.fg)
    root.option_add("*Menu.activeBackground", pal.selection_bg)
    root.option_add("*Menu.activeForeground", pal.selection_fg)
    root.option_add("*Menu.borderWidth", 0)

    try:
        root.configure(bg=pal.window_bg)
    except Exception:  # noqa: BLE001 — non-widget roots should be ignored
        pass

    style_engine = ttk.Style(root)
    # `clam` is the most themable ttk backend — it honors fieldbackground,
    # bordercolor, lightcolor, darkcolor, etc., which the native macOS/Windows
    # themes ignore. We rebuild from there.
    try:
        style_engine.theme_use("clam")
    except Exception:  # noqa: BLE001
        pass

    _configure_ttk(style_engine, pal, family, size)
    return pal


def _configure_ttk(s: ttk.Style, p: Palette, family: str, size: int) -> None:
    base_font = (family, size)
    bold_font = (family, size, "bold")
    title_font = (family, size + 2, "bold")
    header_font = (family, size + 4, "bold")

    # Root defaults — every ttk widget inherits from TWidget / "."
    s.configure(
        ".",
        background=p.window_bg,
        foreground=p.fg,
        fieldbackground=p.view_bg,
        bordercolor=p.border,
        lightcolor=p.border,
        darkcolor=p.border,
        troughcolor=p.window_bg,
        selectbackground=p.selection_bg,
        selectforeground=p.selection_fg,
        insertcolor=p.fg,
        font=base_font,
        focuscolor=p.accent,
    )

    # Frames & labels ---------------------------------------------------------
    s.configure("TFrame", background=p.window_bg)
    s.configure("View.TFrame", background=p.view_bg)
    s.configure("Card.TFrame",
                background=p.view_bg,
                bordercolor=p.border, lightcolor=p.border, darkcolor=p.border,
                relief="solid", borderwidth=1)
    s.configure("HeaderBar.TFrame", background=p.headerbar_bg)

    s.configure("TLabel", background=p.window_bg, foreground=p.fg, font=base_font)
    s.configure("View.TLabel", background=p.view_bg, foreground=p.fg)
    s.configure("Header.TLabel", background=p.headerbar_bg, foreground=p.headerbar_fg, font=bold_font)
    s.configure("Title.TLabel", background=p.window_bg, foreground=p.fg, font=title_font)
    s.configure("LargeTitle.TLabel", background=p.window_bg, foreground=p.fg, font=header_font)
    s.configure("Dim.TLabel", background=p.window_bg, foreground=p.muted_fg)
    s.configure("DimView.TLabel", background=p.view_bg, foreground=p.muted_fg)
    s.configure("Error.TLabel", background=p.window_bg, foreground=p.error)
    s.configure("Success.TLabel", background=p.window_bg, foreground=p.success)

    # Buttons -----------------------------------------------------------------
    btn_pad = (14, 6) if p.style == "gtk4" else (12, 5)
    s.configure(
        "TButton",
        background=p.button_bg,
        foreground=p.fg,
        bordercolor=p.button_border,
        lightcolor=p.button_bg,
        darkcolor=p.button_border,
        focusthickness=1,
        focuscolor=p.accent,
        padding=btn_pad,
        relief="flat",
        borderwidth=1,
        font=base_font,
    )
    s.map(
        "TButton",
        background=[("pressed", p.button_bg_active),
                    ("active", p.button_bg_hover),
                    ("disabled", p.button_bg)],
        foreground=[("disabled", p.dim_fg)],
        bordercolor=[("focus", p.accent), ("active", p.strong_border)],
        lightcolor=[("pressed", p.button_bg_active),
                    ("active", p.button_bg_hover)],
    )

    # Suggested-action (accent) button
    s.configure(
        "Suggested.TButton",
        background=p.accent,
        foreground=p.accent_fg,
        bordercolor=p.accent,
        lightcolor=p.accent,
        darkcolor=p.accent,
        padding=btn_pad,
        relief="flat",
        borderwidth=1,
        font=bold_font,
    )
    s.map(
        "Suggested.TButton",
        background=[("pressed", p.accent_active),
                    ("active", p.accent_hover),
                    ("disabled", p.button_bg)],
        foreground=[("disabled", p.dim_fg)],
        bordercolor=[("pressed", p.accent_active), ("active", p.accent_hover)],
        lightcolor=[("pressed", p.accent_active), ("active", p.accent_hover)],
    )

    # Destructive (red) button
    s.configure(
        "Destructive.TButton",
        background=p.error,
        foreground="#ffffff",
        bordercolor=p.error,
        lightcolor=p.error,
        darkcolor=p.error,
        padding=btn_pad,
        relief="flat",
        borderwidth=1,
        font=bold_font,
    )
    s.map(
        "Destructive.TButton",
        background=[("pressed", "#a51d2d"), ("active", "#e45a62")],
        bordercolor=[("pressed", "#a51d2d"), ("active", "#e45a62")],
        lightcolor=[("pressed", "#a51d2d"), ("active", "#e45a62")],
    )

    # Flat / headerbar button — no border until hovered.
    s.configure(
        "Flat.TButton",
        background=p.headerbar_bg,
        foreground=p.headerbar_fg,
        bordercolor=p.headerbar_bg,
        lightcolor=p.headerbar_bg,
        darkcolor=p.headerbar_bg,
        padding=(10, 6),
        relief="flat",
        borderwidth=1,
        font=base_font,
    )
    s.map(
        "Flat.TButton",
        background=[("pressed", p.button_bg_active),
                    ("active", p.button_bg_hover)],
        bordercolor=[("active", p.border)],
        lightcolor=[("active", p.button_bg_hover)],
    )

    # Link button
    s.configure(
        "Link.TButton",
        background=p.window_bg,
        foreground=p.accent,
        bordercolor=p.window_bg,
        lightcolor=p.window_bg,
        darkcolor=p.window_bg,
        relief="flat",
        borderwidth=0,
        padding=(4, 2),
        font=base_font,
    )
    s.map(
        "Link.TButton",
        foreground=[("pressed", p.accent_active), ("active", p.accent_hover)],
    )

    # Entries & combos --------------------------------------------------------
    s.configure(
        "TEntry",
        fieldbackground=p.view_bg,
        foreground=p.fg,
        bordercolor=p.border,
        lightcolor=p.border,
        darkcolor=p.border,
        insertcolor=p.fg,
        padding=6,
        relief="flat",
        borderwidth=1,
    )
    s.map(
        "TEntry",
        bordercolor=[("focus", p.accent), ("invalid", p.error)],
        lightcolor=[("focus", p.accent)],
        darkcolor=[("focus", p.accent)],
    )

    s.configure(
        "TCombobox",
        fieldbackground=p.view_bg,
        background=p.button_bg,
        foreground=p.fg,
        bordercolor=p.border,
        lightcolor=p.border,
        darkcolor=p.border,
        arrowcolor=p.muted_fg,
        padding=5,
        relief="flat",
    )
    s.map(
        "TCombobox",
        fieldbackground=[("readonly", p.view_bg), ("disabled", p.window_bg)],
        bordercolor=[("focus", p.accent), ("active", p.strong_border)],
        arrowcolor=[("active", p.fg), ("disabled", p.dim_fg)],
    )
    # Drop-down list background — must be set on the hidden Listbox via option_add above.
    root_options = {
        "*TCombobox*Listbox.background": p.view_bg,
        "*TCombobox*Listbox.foreground": p.fg,
        "*TCombobox*Listbox.selectBackground": p.selection_bg,
        "*TCombobox*Listbox.selectForeground": p.selection_fg,
        "*TCombobox*Listbox.borderWidth": 0,
    }
    for k, v in root_options.items():
        s.master.option_add(k, v)

    s.configure(
        "TSpinbox",
        fieldbackground=p.view_bg,
        background=p.button_bg,
        foreground=p.fg,
        bordercolor=p.border,
        lightcolor=p.border,
        darkcolor=p.border,
        arrowcolor=p.muted_fg,
        padding=5,
        relief="flat",
    )
    s.map("TSpinbox", bordercolor=[("focus", p.accent)])

    # Check / radio -----------------------------------------------------------
    s.configure(
        "TCheckbutton",
        background=p.window_bg,
        foreground=p.fg,
        focuscolor=p.accent,
        indicatorcolor=p.view_bg,
        indicatorbackground=p.view_bg,
        padding=4,
    )
    s.map(
        "TCheckbutton",
        background=[("active", p.window_bg)],
        indicatorcolor=[("selected", p.accent), ("pressed", p.accent_active)],
        foreground=[("disabled", p.dim_fg)],
    )
    s.configure("View.TCheckbutton", background=p.view_bg, foreground=p.fg)
    s.map("View.TCheckbutton",
          background=[("active", p.view_bg)],
          indicatorcolor=[("selected", p.accent), ("pressed", p.accent_active)])

    s.configure(
        "TRadiobutton",
        background=p.window_bg,
        foreground=p.fg,
        focuscolor=p.accent,
        indicatorcolor=p.view_bg,
        padding=4,
    )
    s.map(
        "TRadiobutton",
        indicatorcolor=[("selected", p.accent), ("pressed", p.accent_active)],
        background=[("active", p.window_bg)],
    )

    # Notebook ----------------------------------------------------------------
    s.configure("TNotebook", background=p.window_bg, bordercolor=p.border,
                lightcolor=p.border, darkcolor=p.border, tabmargins=(0, 0, 0, 0))
    s.configure(
        "TNotebook.Tab",
        background=p.window_bg,
        foreground=p.muted_fg,
        bordercolor=p.window_bg,
        lightcolor=p.window_bg,
        darkcolor=p.window_bg,
        padding=(14, 8),
        font=base_font,
    )
    s.map(
        "TNotebook.Tab",
        background=[("selected", p.window_bg), ("active", p.button_bg_hover)],
        foreground=[("selected", p.fg), ("active", p.fg)],
        # libadwaita underlines the active tab with the accent
        bordercolor=[("selected", p.accent)],
        lightcolor=[("selected", p.accent)],
    )
    # Only the bottom border of the selected tab should be accent-colored.
    s.layout("TNotebook.Tab", [
        ("Notebook.tab", {"sticky": "nswe", "children": [
            ("Notebook.padding", {"side": "top", "sticky": "nswe", "children": [
                ("Notebook.focus", {"side": "top", "sticky": "nswe", "children": [
                    ("Notebook.label", {"side": "top", "sticky": ""}),
                ]}),
            ]}),
        ]}),
    ])

    # Treeview ----------------------------------------------------------------
    s.configure(
        "Treeview",
        background=p.view_bg,
        fieldbackground=p.view_bg,
        foreground=p.fg,
        bordercolor=p.border,
        lightcolor=p.border,
        darkcolor=p.border,
        rowheight=int(size * 2.4),
        font=base_font,
    )
    s.map(
        "Treeview",
        background=[("selected", p.selection_bg)],
        foreground=[("selected", p.selection_fg)],
    )
    s.configure(
        "Treeview.Heading",
        background=p.headerbar_bg,
        foreground=p.headerbar_fg,
        bordercolor=p.border,
        lightcolor=p.headerbar_bg,
        darkcolor=p.border,
        relief="flat",
        padding=(8, 6),
        font=bold_font,
    )
    s.map("Treeview.Heading",
          background=[("active", p.button_bg_hover)])

    # Scrollbars --------------------------------------------------------------
    s.configure(
        "TScrollbar",
        background=p.window_bg,
        troughcolor=p.window_bg,
        bordercolor=p.window_bg,
        arrowcolor=p.muted_fg,
        gripcount=0,
        relief="flat",
        borderwidth=0,
    )
    s.map(
        "TScrollbar",
        background=[("active", p.strong_border), ("!active", p.border)],
        arrowcolor=[("disabled", p.dim_fg), ("active", p.fg)],
    )
    s.configure("Vertical.TScrollbar", arrowsize=14)
    s.configure("Horizontal.TScrollbar", arrowsize=14)

    # Progressbar -------------------------------------------------------------
    s.configure(
        "TProgressbar",
        background=p.accent,
        troughcolor=p.button_bg,
        bordercolor=p.border,
        lightcolor=p.accent,
        darkcolor=p.accent,
        thickness=8 if p.style == "gtk4" else 10,
    )
    s.configure("Horizontal.TProgressbar", background=p.accent)
    s.configure("Vertical.TProgressbar", background=p.accent)

    # Scale -------------------------------------------------------------------
    s.configure(
        "TScale",
        background=p.window_bg,
        troughcolor=p.button_bg_active,
        bordercolor=p.border,
        lightcolor=p.accent,
        darkcolor=p.accent,
    )
    s.map("TScale", background=[("active", p.window_bg)])

    # Separator ---------------------------------------------------------------
    s.configure("TSeparator", background=p.border)

    # Labelframe --------------------------------------------------------------
    s.configure("TLabelframe",
                background=p.window_bg,
                bordercolor=p.border,
                lightcolor=p.border,
                darkcolor=p.border,
                relief="solid",
                borderwidth=1)
    s.configure("TLabelframe.Label",
                background=p.window_bg, foreground=p.fg, font=bold_font)

    # Paned window ------------------------------------------------------------
    s.configure("TPanedwindow", background=p.window_bg)
    s.configure("Sash", sashthickness=6, background=p.border)
