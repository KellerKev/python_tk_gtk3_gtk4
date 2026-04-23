"""Showcase window for the GTK skin.

Run with:
    pixi run demo            # default GTK4 light
    pixi run demo3           # GTK3 Adwaita
    pixi run demo4           # GTK4 libadwaita
    pixi run demo-dark       # GTK4 dark
"""

from __future__ import annotations

import argparse
import tkinter as tk
from tkinter import ttk

from .theme import apply_skin
from .widgets import (
    Avatar, Check, HeaderBar, ListBox, ListRow, PillButton, Radio, Scale,
    Separator, Switch,
)


def build(root: tk.Tk, style: str, dark: bool) -> None:
    pal = apply_skin(root, style=style, dark=dark)  # type: ignore[arg-type]

    root.title(f"GTK Skin · {pal.name}")
    root.geometry("780x620")
    root.configure(bg=pal.window_bg)

    # --- Header bar ------------------------------------------------------
    header = HeaderBar(
        root, pal,
        title="Preferences",
        subtitle="Demo of the tkinter GTK skin",
    )
    header.pack(fill="x")

    # Leading: sidebar toggle (flat icon button)
    ttk.Button(header.leading, text="☰", style="Flat.TButton", width=3).pack(side="left")

    # Trailing: search + menu + suggested "Save"
    ttk.Button(header.trailing, text="⌕", style="Flat.TButton", width=3).pack(side="left", padx=2)
    ttk.Button(header.trailing, text="⋮", style="Flat.TButton", width=3).pack(side="left", padx=2)

    # --- Body ------------------------------------------------------------
    body = ttk.Frame(root, style="TFrame")
    body.pack(fill="both", expand=True)

    notebook = ttk.Notebook(body)
    notebook.pack(fill="both", expand=True, padx=16, pady=16)

    notebook.add(_build_general_tab(notebook, pal), text="General")
    notebook.add(_build_controls_tab(notebook, pal), text="Controls")
    notebook.add(_build_data_tab(notebook, pal), text="Data")
    notebook.add(_build_about_tab(notebook, pal), text="About")

    # --- Footer with style switcher -------------------------------------
    footer = ttk.Frame(root, style="TFrame")
    footer.pack(fill="x", side="bottom", padx=16, pady=(0, 16))

    ttk.Label(footer, text=f"Theme: {pal.name}", style="Dim.TLabel").pack(side="left")

    def restart(new_style: str, new_dark: bool) -> None:
        for w in root.winfo_children():
            w.destroy()
        build(root, new_style, new_dark)

    ttk.Button(footer, text="GTK3",
               command=lambda: restart("gtk3", dark)).pack(side="right", padx=4)
    ttk.Button(footer, text="GTK4",
               command=lambda: restart("gtk4", dark)).pack(side="right", padx=4)
    ttk.Button(footer, text="Light" if dark else "Dark",
               style="Suggested.TButton",
               command=lambda: restart(style, not dark)).pack(side="right", padx=4)


def _build_general_tab(parent, pal) -> ttk.Frame:
    tab = ttk.Frame(parent, style="TFrame", padding=(4, 12))

    ttk.Label(tab, text="Appearance", style="Title.TLabel").pack(anchor="w", pady=(0, 8))

    appearance = ListBox(tab, pal)
    appearance.pack(fill="x", pady=(0, 20))
    appearance.add_row(ListRow(
        appearance.container, pal,
        title="Dark mode",
        subtitle="Use a dark color palette throughout the app",
        trailing=lambda parent: Switch(parent, pal),
    ))
    appearance.add_row(ListRow(
        appearance.container, pal,
        title="Reduce animations",
        subtitle="Turn off non-essential motion",
        trailing=lambda parent: Switch(parent, pal),
    ))

    def accent_combo(parent):
        cb = ttk.Combobox(
            parent,
            values=["Blue", "Teal", "Green", "Yellow", "Orange", "Red", "Purple"],
            state="readonly", width=10,
        )
        cb.current(0)
        return cb

    appearance.add_row(ListRow(
        appearance.container, pal,
        title="Accent color",
        subtitle="Applies to buttons, switches, and selection",
        trailing=accent_combo,
    ))

    ttk.Label(tab, text="Account", style="Title.TLabel").pack(anchor="w", pady=(0, 8))

    account = ListBox(tab, pal)
    account.pack(fill="x", pady=(0, 20))

    # Avatar row with name/email beside it — build manually so the avatar
    # sits where the icon slot normally would.
    avatar_row = tk.Frame(account.container, bg=pal.view_bg)
    # Right-side button first so the label column doesn't consume all space.
    ttk.Button(avatar_row, text="Sign out", style="Flat.TButton").pack(
        side="right", padx=(8, 14), pady=12)
    Avatar(avatar_row, pal, text="KK", size=44).pack(side="left", padx=(14, 12), pady=12)
    meta = tk.Frame(avatar_row, bg=pal.view_bg)
    meta.pack(side="left", fill="x", expand=True, pady=12)
    tk.Label(meta, text="Kevin Keller", bg=pal.view_bg, fg=pal.fg,
             font=(None, 12, "bold"), anchor="w").pack(anchor="w")
    tk.Label(meta, text="kevin@fineupp.com", bg=pal.view_bg, fg=pal.muted_fg,
             font=(None, 10), anchor="w").pack(anchor="w")
    account.add_row(avatar_row)

    sync_var = tk.BooleanVar(value=True)
    account.add_row(ListRow(
        account.container, pal,
        title="Sync",
        subtitle="Last synced 2 minutes ago",
        trailing=lambda parent: Switch(parent, pal, variable=sync_var),
    ))

    return tab


def _build_controls_tab(parent, pal) -> ttk.Frame:
    tab = ttk.Frame(parent, style="TFrame", padding=16)

    # Buttons row
    ttk.Label(tab, text="Buttons", style="Title.TLabel").grid(
        row=0, column=0, sticky="w", pady=(0, 8), columnspan=3)

    btn_row = ttk.Frame(tab, style="TFrame")
    btn_row.grid(row=1, column=0, sticky="w", columnspan=3, pady=(0, 20))
    ttk.Button(btn_row, text="Default").pack(side="left", padx=4)
    ttk.Button(btn_row, text="Save", style="Suggested.TButton").pack(side="left", padx=4)
    ttk.Button(btn_row, text="Delete", style="Destructive.TButton").pack(side="left", padx=4)
    ttk.Button(btn_row, text="Learn more", style="Link.TButton").pack(side="left", padx=4)
    PillButton(btn_row, pal, text="Pill", kind="accent").pack(side="left", padx=6)
    PillButton(btn_row, pal, text="Neutral", kind="flat").pack(side="left", padx=4)

    # Entries
    ttk.Label(tab, text="Text input", style="Title.TLabel").grid(
        row=2, column=0, sticky="w", pady=(0, 8), columnspan=3)

    ttk.Label(tab, text="Name").grid(row=3, column=0, sticky="w", padx=(0, 8))
    entry_name = ttk.Entry(tab, width=28)
    entry_name.insert(0, "Kevin")
    entry_name.grid(row=3, column=1, sticky="w", pady=3)

    ttk.Label(tab, text="Password").grid(row=4, column=0, sticky="w", padx=(0, 8))
    ttk.Entry(tab, width=28, show="•").grid(row=4, column=1, sticky="w", pady=3)

    ttk.Label(tab, text="Language").grid(row=5, column=0, sticky="w", padx=(0, 8))
    lang = ttk.Combobox(tab, values=["English", "French", "German", "日本語"],
                        state="readonly", width=26)
    lang.current(0)
    lang.grid(row=5, column=1, sticky="w", pady=3)

    ttk.Label(tab, text="Level").grid(row=6, column=0, sticky="w", padx=(0, 8))
    ttk.Spinbox(tab, from_=0, to=100, width=26).grid(row=6, column=1, sticky="w", pady=3)

    Separator(tab, pal).grid(row=7, column=0, columnspan=3, sticky="ew", pady=16)

    # Checkboxes / radios / scale / progress
    ttk.Label(tab, text="Toggles", style="Title.TLabel").grid(
        row=8, column=0, sticky="w", pady=(0, 8), columnspan=3)

    Check(tab, pal, text="Enable notifications",
          variable=tk.BooleanVar(value=True)).grid(row=9, column=0, sticky="w")
    Check(tab, pal, text="Auto-update apps",
          variable=tk.BooleanVar(value=False)).grid(row=9, column=1, sticky="w")

    rv = tk.StringVar(value="balanced")
    Radio(tab, pal, text="Performance", variable=rv, value="perf").grid(
        row=10, column=0, sticky="w", pady=4)
    Radio(tab, pal, text="Balanced", variable=rv, value="balanced").grid(
        row=10, column=1, sticky="w", pady=4)
    Radio(tab, pal, text="Power saver", variable=rv, value="power").grid(
        row=10, column=2, sticky="w", pady=4)

    ttk.Label(tab, text="Volume").grid(row=11, column=0, sticky="w", pady=(12, 0))
    Scale(tab, pal, from_=0, to=100, value=60, length=240).grid(
        row=11, column=1, sticky="w", columnspan=2, pady=(12, 0))

    ttk.Label(tab, text="Sync progress").grid(row=12, column=0, sticky="w", pady=(8, 0))
    pb = ttk.Progressbar(tab, mode="determinate", value=60, length=240)
    pb.grid(row=12, column=1, sticky="w", columnspan=2, pady=(8, 0))

    return tab


def _build_data_tab(parent, pal) -> ttk.Frame:
    tab = ttk.Frame(parent, style="TFrame", padding=16)
    ttk.Label(tab, text="Recent activity", style="Title.TLabel").pack(anchor="w", pady=(0, 8))

    columns = ("when", "action", "user", "status")
    tree = ttk.Treeview(tab, columns=columns, show="headings", height=10)
    tree.heading("when", text="When")
    tree.heading("action", text="Action")
    tree.heading("user", text="User")
    tree.heading("status", text="Status")
    tree.column("when", width=140)
    tree.column("action", width=220)
    tree.column("user", width=160)
    tree.column("status", width=100)

    rows = [
        ("2m ago",  "Pushed commit to main",       "kevin",  "Success"),
        ("14m ago", "Opened pull request #482",    "alice",  "Open"),
        ("1h ago",  "Deployed v1.12.3 to prod",    "bot",    "Success"),
        ("3h ago",  "Reviewed PR #480",            "bob",    "Changes"),
        ("1d ago",  "Archived old feature branch", "kevin",  "Success"),
        ("2d ago",  "Failed CI run",               "bot",    "Failed"),
    ]
    for r in rows:
        tree.insert("", "end", values=r)

    sb = ttk.Scrollbar(tab, orient="vertical", command=tree.yview)
    tree.configure(yscrollcommand=sb.set)
    tree.pack(side="left", fill="both", expand=True)
    sb.pack(side="right", fill="y")

    return tab


def _build_about_tab(parent, pal) -> ttk.Frame:
    tab = ttk.Frame(parent, style="TFrame", padding=32)

    Avatar(tab, pal, text="GS", size=72, color=pal.accent).pack(pady=(12, 12))
    ttk.Label(tab, text="GTK Skin for Tkinter", style="LargeTitle.TLabel").pack()
    ttk.Label(tab, text="Version 0.1.0", style="Dim.TLabel").pack(pady=(0, 16))

    ttk.Label(
        tab,
        style="TLabel",
        text=(
            "A tkinter skin that mimics the look of GTK3 (Adwaita) and\n"
            "GTK4 (libadwaita). Use it for Python desktop tools that should\n"
            "fit in on GNOME without the PyGObject dependency."
        ),
        justify="center",
    ).pack(pady=(0, 20))

    row = ttk.Frame(tab, style="TFrame")
    row.pack()
    ttk.Button(row, text="Website", style="Link.TButton").pack(side="left", padx=6)
    ttk.Button(row, text="Report issue", style="Link.TButton").pack(side="left", padx=6)
    ttk.Button(row, text="Credits", style="Link.TButton").pack(side="left", padx=6)

    return tab


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--style", choices=("gtk3", "gtk4"), default="gtk4")
    parser.add_argument("--dark", action="store_true")
    args = parser.parse_args()

    root = tk.Tk()
    build(root, args.style, args.dark)
    root.mainloop()


if __name__ == "__main__":
    main()
