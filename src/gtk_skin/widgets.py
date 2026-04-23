"""Custom Tk widgets that fill gaps ttk can't cover (rounded shapes, switches)."""

from __future__ import annotations

import tkinter as tk
from tkinter import ttk
from typing import Callable, Optional

from .theme import Palette


def _parent_bg(master, fallback: str) -> str:
    """Return the master's background color, or `fallback` if master is a ttk
    widget (ttk widgets don't accept `-bg`)."""
    try:
        return master.cget("bg")
    except tk.TclError:
        pass
    try:
        style_name = master.cget("style") or master.winfo_class()
        return ttk.Style(master).lookup(style_name, "background") or fallback
    except tk.TclError:
        return fallback


# ---------------------------------------------------------------------------
# Canvas primitives
# ---------------------------------------------------------------------------

def _rounded_rect_points(x1: float, y1: float, x2: float, y2: float, r: float) -> list[float]:
    """Return polygon points that trace a rounded rectangle.

    Tk canvas has no native rounded rect; we fake it with a smoothed polygon.
    The repeated corner points give the smoothing spline sharp tangents at the
    flats and curves at the corners.
    """
    r = min(r, (x2 - x1) / 2, (y2 - y1) / 2)
    return [
        x1 + r, y1,
        x2 - r, y1,
        x2 - r, y1,
        x2,     y1,
        x2,     y1 + r,
        x2,     y2 - r,
        x2,     y2 - r,
        x2,     y2,
        x2 - r, y2,
        x1 + r, y2,
        x1 + r, y2,
        x1,     y2,
        x1,     y2 - r,
        x1,     y1 + r,
        x1,     y1 + r,
        x1,     y1,
        x1 + r, y1,
    ]


def draw_rounded_rect(canvas: tk.Canvas, x1, y1, x2, y2, r, **kwargs):
    return canvas.create_polygon(
        _rounded_rect_points(x1, y1, x2, y2, r), smooth=True, **kwargs
    )


# ---------------------------------------------------------------------------
# HeaderBar
# ---------------------------------------------------------------------------

class HeaderBar(tk.Frame):
    """A GTK-style window header bar.

    Contains a title label (optionally with a subtitle), plus `.leading` and
    `.trailing` frames for packing icon/flat buttons like GNOME apps do.

    Example:
        hb = HeaderBar(root, palette, title="My App")
        ttk.Button(hb.trailing, text="☰", style="Flat.TButton").pack(side="right")
        hb.pack(fill="x")
    """

    def __init__(
        self,
        master,
        palette: Palette,
        *,
        title: str = "",
        subtitle: str = "",
        **kwargs,
    ):
        super().__init__(
            master,
            bg=palette.headerbar_bg,
            highlightthickness=0,
            bd=0,
            **kwargs,
        )
        self._palette = palette

        # 1px bottom border — the subtle line that separates the headerbar
        # from the window content in both GTK3 and GTK4.
        border = tk.Frame(self, bg=palette.headerbar_border, height=1)
        border.pack(side="bottom", fill="x")

        inner = tk.Frame(self, bg=palette.headerbar_bg, height=palette.header_height)
        inner.pack(fill="both", expand=True)
        inner.pack_propagate(False)

        self.leading = tk.Frame(inner, bg=palette.headerbar_bg)
        self.leading.pack(side="left", padx=(8, 0), pady=6)

        self.trailing = tk.Frame(inner, bg=palette.headerbar_bg)
        self.trailing.pack(side="right", padx=(0, 8), pady=6)

        self._title_frame = tk.Frame(inner, bg=palette.headerbar_bg)
        self._title_frame.pack(expand=True)

        self._title_var = tk.StringVar(value=title)
        self._subtitle_var = tk.StringVar(value=subtitle)

        # GTK4 uses a single bold centered title. GTK3 stacks title + subtitle.
        if palette.style == "gtk4":
            self._title_label = tk.Label(
                self._title_frame,
                textvariable=self._title_var,
                bg=palette.headerbar_bg,
                fg=palette.headerbar_fg,
                font=(_font_family(self), 11, "bold"),
            )
            self._title_label.pack()
            self._subtitle_label = None
        else:
            self._title_label = tk.Label(
                self._title_frame,
                textvariable=self._title_var,
                bg=palette.headerbar_bg,
                fg=palette.headerbar_fg,
                font=(_font_family(self), 11, "bold"),
            )
            self._title_label.pack()
            self._subtitle_label = tk.Label(
                self._title_frame,
                textvariable=self._subtitle_var,
                bg=palette.headerbar_bg,
                fg=palette.muted_fg,
                font=(_font_family(self), 9),
            )
            if subtitle:
                self._subtitle_label.pack()

    def set_title(self, title: str, subtitle: str = "") -> None:
        self._title_var.set(title)
        self._subtitle_var.set(subtitle)
        if self._subtitle_label is not None:
            if subtitle and not self._subtitle_label.winfo_ismapped():
                self._subtitle_label.pack()
            elif not subtitle and self._subtitle_label.winfo_ismapped():
                self._subtitle_label.pack_forget()


def _font_family(widget) -> str:
    # Inherit whatever family apply_skin picked via option_add.
    try:
        return widget.tk.call("option", "get", widget, "font", "Font") or "TkDefaultFont"
    except tk.TclError:
        return "TkDefaultFont"


# ---------------------------------------------------------------------------
# Switch — GNOME-style pill toggle
# ---------------------------------------------------------------------------

class Switch(tk.Canvas):
    """Rounded toggle switch modeled after GNOME Settings.

    Use `.get()` / `.set(bool)` to read/write state, or pass `command` to be
    notified on change. `variable` binds to a `tk.BooleanVar`.
    """

    def __init__(
        self,
        master,
        palette: Palette,
        *,
        variable: Optional[tk.BooleanVar] = None,
        command: Optional[Callable[[bool], None]] = None,
        width: int = 44,
        height: int = 24,
        **kwargs,
    ):
        # Headers use view_bg too; we look it up dynamically at draw-time.
        self._palette = palette
        self._state = bool(variable.get()) if variable is not None else False
        self._command = command
        self._var = variable
        # NOTE: tkinter.Misc uses self._w internally for the Tcl widget path,
        # so we store our canvas size under different names.
        self._cw = width
        self._ch = height

        super().__init__(
            master,
            width=width,
            height=height,
            highlightthickness=0,
            bd=0,
            bg=kwargs.pop("bg", _parent_bg(master, palette.window_bg)),
            **kwargs,
        )
        self.bind("<Button-1>", self._toggle)
        self.bind("<Configure>", lambda _e: self._redraw())

        if self._var is not None:
            self._trace_id = self._var.trace_add("write", lambda *_: self._sync_from_var())
        else:
            self._trace_id = None

        self._redraw()

    # -- state ------------------------------------------------------------
    def get(self) -> bool:
        return self._state

    def set(self, value: bool) -> None:
        value = bool(value)
        if value == self._state:
            return
        self._state = value
        if self._var is not None and self._var.get() != value:
            self._var.set(value)
        self._redraw()

    def _sync_from_var(self) -> None:
        if self._var is None:
            return
        new_val = bool(self._var.get())
        if new_val != self._state:
            self._state = new_val
            self._redraw()

    def _toggle(self, _event=None) -> None:
        self.set(not self._state)
        if self._command is not None:
            self._command(self._state)

    # -- drawing ----------------------------------------------------------
    def _redraw(self) -> None:
        self.delete("all")
        p = self._palette
        w, h = self._cw, self._ch
        r = h / 2 - 1

        track_color = p.accent if self._state else p.button_bg_active
        # On a view background, libadwaita uses a softer off-state; keep it
        # readable by darkening button_bg slightly.
        if not self._state and p.dark:
            track_color = "#5a5a5a"
        knob_color = "#ffffff"

        draw_rounded_rect(self, 1, 1, w - 1, h - 1, r, fill=track_color, outline="")

        knob_margin = 3
        knob_size = h - 2 * knob_margin
        if self._state:
            x = w - knob_margin - knob_size
        else:
            x = knob_margin
        self.create_oval(x, knob_margin, x + knob_size, knob_margin + knob_size,
                         fill=knob_color, outline="")


# ---------------------------------------------------------------------------
# PillButton — rounded accent button (GTK4 loves these)
# ---------------------------------------------------------------------------

class PillButton(tk.Canvas):
    """Rounded accent button. Useful where ttk buttons' corners look square.

    `kind` = "accent" | "flat" | "destructive"
    """

    def __init__(
        self,
        master,
        palette: Palette,
        text: str = "Button",
        *,
        kind: str = "accent",
        command: Optional[Callable[[], None]] = None,
        padx: int = 16,
        pady: int = 8,
        **kwargs,
    ):
        self._palette = palette
        self._text = text
        self._kind = kind
        self._command = command
        self._pressed = False
        self._hover = False
        self._enabled = True

        # Measure text so the canvas picks a tight width. Using tkfont
        # directly avoids creating a probe widget under a ttk parent.
        from tkinter import font as _tkfont
        probe_font = _tkfont.Font(family=_font_family(master), size=11, weight="bold")
        text_w = probe_font.measure(text)
        text_h = probe_font.metrics("linespace")

        w = text_w + padx * 2
        h = text_h + pady * 2

        super().__init__(
            master,
            width=w,
            height=h,
            highlightthickness=0,
            bd=0,
            bg=kwargs.pop("bg", _parent_bg(master, palette.window_bg)),
            **kwargs,
        )
        # See Switch for why we avoid the name self._w.
        self._cw, self._ch = w, h

        self.bind("<Button-1>", self._on_press)
        self.bind("<ButtonRelease-1>", self._on_release)
        self.bind("<Enter>", self._on_enter)
        self.bind("<Leave>", self._on_leave)
        self._redraw()

    def configure_state(self, enabled: bool) -> None:
        self._enabled = enabled
        self._redraw()

    def set_text(self, text: str) -> None:
        self._text = text
        self._redraw()

    # -- events -----------------------------------------------------------
    def _on_press(self, _e):
        if not self._enabled:
            return
        self._pressed = True
        self._redraw()

    def _on_release(self, e):
        if not self._enabled:
            return
        was_pressed = self._pressed
        self._pressed = False
        self._redraw()
        if was_pressed and 0 <= e.x <= self._cw and 0 <= e.y <= self._ch:
            if self._command is not None:
                self._command()

    def _on_enter(self, _e):
        self._hover = True
        self._redraw()

    def _on_leave(self, _e):
        self._hover = False
        self._pressed = False
        self._redraw()

    # -- drawing ----------------------------------------------------------
    def _colors(self) -> tuple[str, str]:
        p = self._palette
        if not self._enabled:
            return p.button_bg, p.dim_fg
        if self._kind == "accent":
            if self._pressed:
                return p.accent_active, p.accent_fg
            if self._hover:
                return p.accent_hover, p.accent_fg
            return p.accent, p.accent_fg
        if self._kind == "destructive":
            if self._pressed:
                return "#a51d2d", "#ffffff"
            if self._hover:
                return "#e45a62", "#ffffff"
            return p.error, "#ffffff"
        # flat
        if self._pressed:
            return p.button_bg_active, p.fg
        if self._hover:
            return p.button_bg_hover, p.fg
        return p.button_bg, p.fg

    def _redraw(self):
        self.delete("all")
        bg, fg = self._colors()
        r = min(self._ch / 2, self._palette.radius + (6 if self._palette.style == "gtk4" else 2))
        draw_rounded_rect(self, 1, 1, self._cw - 1, self._ch - 1, r, fill=bg, outline="")
        self.create_text(
            self._cw / 2, self._ch / 2,
            text=self._text,
            fill=fg,
            font=(_font_family(self), 11, "bold"),
        )


# ---------------------------------------------------------------------------
# ListBox & ListRow — GNOME preferences-style rows
# ---------------------------------------------------------------------------

class ListBox(tk.Frame):
    """Container for ListRow widgets. Draws a rounded, bordered card that
    contains its children with separators between rows — the shape that
    dominates GNOME Settings / Adwaita preferences.

    Add rows via `add_row(ListRow(...))` or just pack ListRow instances
    directly as children.
    """

    def __init__(self, master, palette: Palette, **kwargs):
        self._palette = palette
        super().__init__(
            master,
            bg=palette.window_bg,
            highlightthickness=0,
            bd=0,
            **kwargs,
        )

        # Outer canvas draws the rounded border around the whole list.
        self._canvas = tk.Canvas(
            self,
            bg=palette.window_bg,
            highlightthickness=0,
            bd=0,
        )
        self._canvas.pack(fill="both", expand=True)

        # Inner frame holds the actual rows. Expose it as `.container` so
        # callers can create rows directly parented to it — pack(in_=…)
        # across different masters is unreliable for descendants like
        # canvas-based Switches.
        self._inner = tk.Frame(self._canvas, bg=palette.view_bg)
        self._window = self._canvas.create_window(0, 0, anchor="nw", window=self._inner)
        self.container = self._inner

        self._inner.bind("<Configure>", self._on_inner_configure)
        self._canvas.bind("<Configure>", self._on_canvas_configure)
        self._rows: list[tk.Widget] = []

    def add_row(self, row: tk.Widget) -> None:
        if self._rows:
            sep = tk.Frame(self._inner, bg=self._palette.border, height=1)
            sep.pack(fill="x")
            row._gtk_separator = sep  # type: ignore[attr-defined]
        # If row was created parented to self (the ListBox) instead of
        # self.container, use pack(in_=…) as a fallback — it works for
        # Frames even though it's unreliable for some canvas widgets.
        row.pack(in_=self._inner, fill="x")
        self._rows.append(row)

    def _on_inner_configure(self, _e):
        self._canvas.configure(scrollregion=self._canvas.bbox("all"))
        self._draw_border()

    def _on_canvas_configure(self, e):
        self._canvas.itemconfigure(self._window, width=e.width)
        self._draw_border()

    def _draw_border(self):
        self._canvas.delete("border")
        p = self._palette
        w = self._canvas.winfo_width()
        h = self._inner.winfo_reqheight()
        if w <= 2 or h <= 2:
            return
        self._canvas.configure(height=h)
        # Fill behind everything so corners blend with window bg.
        self._canvas.create_rectangle(
            0, 0, w, h, fill=p.window_bg, outline="", tags="border",
        )
        draw_rounded_rect(
            self._canvas, 1, 1, w - 1, h - 1, p.radius,
            fill=p.view_bg, outline=p.border, width=1, tags="border",
        )
        self._canvas.tag_lower("border")


class ListRow(tk.Frame):
    """A single row for use inside a ListBox.

    Contains a title, optional subtitle on the left, and accepts a trailing
    widget (switch, label, button) on the right via the `trailing` factory
    or by creating widgets directly with `row.trailing_frame` as parent.

    `trailing` is a callable `(parent_frame) -> widget` so the trailing
    widget is parented to the correct frame (needed for reliable geometry).
    """

    def __init__(
        self,
        master,
        palette: Palette,
        *,
        title: str = "",
        subtitle: str = "",
        trailing: Optional[Callable[[tk.Frame], tk.Widget]] = None,
        icon: str = "",
        **kwargs,
    ):
        self._palette = palette
        super().__init__(
            master,
            bg=palette.view_bg,
            highlightthickness=0,
            bd=0,
            **kwargs,
        )

        pad_y = 10 if palette.style == "gtk4" else 8

        # Pack trailing frame FIRST so it reserves right-edge space before the
        # expanding label column claims everything.
        self.trailing_frame = tk.Frame(self, bg=palette.view_bg)
        self.trailing_frame.pack(side="right", padx=(8, 14), pady=pad_y)

        if icon:
            tk.Label(
                self, text=icon, bg=palette.view_bg, fg=palette.muted_fg,
                font=(_font_family(self), 14),
            ).pack(side="left", padx=(14, 8), pady=pad_y)

        labels = tk.Frame(self, bg=palette.view_bg)
        labels.pack(side="left", fill="x", expand=True,
                    padx=(14 if not icon else 0, 8), pady=pad_y)
        tk.Label(
            labels,
            text=title,
            bg=palette.view_bg,
            fg=palette.fg,
            anchor="w",
            font=(_font_family(self), 11, "bold"),
        ).pack(anchor="w")
        if subtitle:
            tk.Label(
                labels,
                text=subtitle,
                bg=palette.view_bg,
                fg=palette.muted_fg,
                anchor="w",
                font=(_font_family(self), 10),
            ).pack(anchor="w")

        if trailing is not None:
            widget = trailing(self.trailing_frame)
            if not widget.winfo_ismapped():
                widget.pack(side="right")


# ---------------------------------------------------------------------------
# Avatar — circular initials
# ---------------------------------------------------------------------------

class Avatar(tk.Canvas):
    def __init__(
        self,
        master,
        palette: Palette,
        *,
        text: str = "?",
        size: int = 40,
        color: Optional[str] = None,
        **kwargs,
    ):
        super().__init__(
            master,
            width=size,
            height=size,
            highlightthickness=0,
            bd=0,
            bg=kwargs.pop("bg", _parent_bg(master, palette.window_bg)),
            **kwargs,
        )
        bg = color or palette.accent
        self.create_oval(1, 1, size - 1, size - 1, fill=bg, outline="")
        # Pick a readable text size relative to avatar size.
        self.create_text(
            size / 2, size / 2 + 1,
            text=text[:2].upper(),
            fill=palette.accent_fg,
            font=(_font_family(self), int(size * 0.4), "bold"),
        )


# ---------------------------------------------------------------------------
# Separator — thin GTK-colored divider
# ---------------------------------------------------------------------------

class Separator(tk.Frame):
    def __init__(self, master, palette: Palette, orient: str = "horizontal", **kwargs):
        if orient == "horizontal":
            kwargs.setdefault("height", 1)
        else:
            kwargs.setdefault("width", 1)
        super().__init__(master, bg=palette.border, bd=0, highlightthickness=0, **kwargs)


# ---------------------------------------------------------------------------
# Radio — canvas-drawn GNOME-style radio button
# ---------------------------------------------------------------------------

class Radio(tk.Frame):
    """GNOME-style radio button. API mirrors ttk.Radiobutton:
        Radio(master, palette, text=..., variable=strvar, value="a")
    """

    def __init__(
        self,
        master,
        palette: Palette,
        *,
        text: str = "",
        variable: tk.StringVar,
        value: str,
        command: Optional[Callable[[], None]] = None,
        **kwargs,
    ):
        bg = _parent_bg(master, palette.window_bg)
        super().__init__(master, bg=bg, bd=0, highlightthickness=0, **kwargs)
        self._palette = palette
        self._var = variable
        self._value = value
        self._command = command
        self._hover = False
        self._bg = bg

        size = 18
        self._indicator = tk.Canvas(
            self, width=size, height=size,
            bg=bg, bd=0, highlightthickness=0,
        )
        self._indicator.pack(side="left", padx=(0, 8))

        self._label = tk.Label(
            self, text=text, bg=bg, fg=palette.fg,
            font=(_font_family(self), 11),
        )
        self._label.pack(side="left")

        for w in (self, self._indicator, self._label):
            w.bind("<Button-1>", self._select)
            w.bind("<Enter>", self._on_enter)
            w.bind("<Leave>", self._on_leave)

        self._var.trace_add("write", lambda *_: self._redraw())
        self._redraw()

    def _select(self, _e=None):
        self._var.set(self._value)
        if self._command is not None:
            self._command()

    def _on_enter(self, _e):
        self._hover = True
        self._redraw()

    def _on_leave(self, _e):
        self._hover = False
        self._redraw()

    def _redraw(self):
        p = self._palette
        c = self._indicator
        c.delete("all")
        selected = self._var.get() == self._value

        # Outer circle: 2px stroke, subtly thicker border on hover.
        border = p.accent if selected else (p.strong_border if self._hover else p.border)
        fill = p.accent if selected else p.view_bg
        c.create_oval(1, 1, 17, 17, outline=border, width=2, fill=fill)
        if selected:
            # White inner dot — the classic GNOME filled-dot look.
            c.create_oval(6, 6, 12, 12, fill="#ffffff", outline="")


# ---------------------------------------------------------------------------
# Check — canvas-drawn GNOME-style checkbox (bonus, since Radio is here)
# ---------------------------------------------------------------------------

class Check(tk.Frame):
    """GNOME-style checkbox backed by a BooleanVar."""

    def __init__(
        self,
        master,
        palette: Palette,
        *,
        text: str = "",
        variable: Optional[tk.BooleanVar] = None,
        command: Optional[Callable[[bool], None]] = None,
        **kwargs,
    ):
        bg = _parent_bg(master, palette.window_bg)
        super().__init__(master, bg=bg, bd=0, highlightthickness=0, **kwargs)
        self._palette = palette
        self._var = variable if variable is not None else tk.BooleanVar(value=False)
        self._command = command
        self._hover = False

        size = 18
        self._indicator = tk.Canvas(
            self, width=size, height=size,
            bg=bg, bd=0, highlightthickness=0,
        )
        self._indicator.pack(side="left", padx=(0, 8))

        self._label = tk.Label(
            self, text=text, bg=bg, fg=palette.fg,
            font=(_font_family(self), 11),
        )
        self._label.pack(side="left")

        for w in (self, self._indicator, self._label):
            w.bind("<Button-1>", self._toggle)
            w.bind("<Enter>", self._on_enter)
            w.bind("<Leave>", self._on_leave)

        self._var.trace_add("write", lambda *_: self._redraw())
        self._redraw()

    def _toggle(self, _e=None):
        self._var.set(not bool(self._var.get()))
        if self._command is not None:
            self._command(bool(self._var.get()))

    def _on_enter(self, _e):
        self._hover = True
        self._redraw()

    def _on_leave(self, _e):
        self._hover = False
        self._redraw()

    def _redraw(self):
        p = self._palette
        c = self._indicator
        c.delete("all")
        checked = bool(self._var.get())

        border = p.accent if checked else (p.strong_border if self._hover else p.border)
        fill = p.accent if checked else p.view_bg
        # Small rounded square (radius 4 to match GTK4's 9px window radius feel).
        draw_rounded_rect(c, 1, 1, 17, 17, r=4, fill=fill, outline=border, width=2)
        if checked:
            # Checkmark: two-segment polyline.
            c.create_line(5, 9, 8, 12, 13, 6, fill="#ffffff", width=2, capstyle="round")


# ---------------------------------------------------------------------------
# Scale — canvas-drawn GNOME-style slider
# ---------------------------------------------------------------------------

class Scale(tk.Canvas):
    """GNOME-style slider with a filled accent portion and a circular knob.

    Mirrors ttk.Scale API:
        Scale(master, palette, from_=0, to=100, value=50, length=200,
              variable=doublevar, command=callable)
    """

    def __init__(
        self,
        master,
        palette: Palette,
        *,
        from_: float = 0,
        to: float = 100,
        value: float = 0,
        variable: Optional[tk.DoubleVar] = None,
        length: int = 220,
        command: Optional[Callable[[float], None]] = None,
        **kwargs,
    ):
        self._palette = palette
        self._from = float(from_)
        self._to = float(to)
        self._var = variable
        if self._var is not None:
            initial = float(self._var.get())
        else:
            initial = float(value)
        self._value = max(self._from, min(self._to, initial))
        self._command = command
        self._dragging = False
        self._hover = False

        height = 22  # enough for the knob + trough
        self._cw = length
        self._ch = height
        bg = _parent_bg(master, palette.window_bg)
        super().__init__(
            master,
            width=length,
            height=height,
            bg=kwargs.pop("bg", bg),
            highlightthickness=0,
            bd=0,
            **kwargs,
        )

        self.bind("<Button-1>", self._on_press)
        self.bind("<B1-Motion>", self._on_drag)
        self.bind("<ButtonRelease-1>", self._on_release)
        self.bind("<Enter>", self._on_enter)
        self.bind("<Leave>", self._on_leave)
        self.bind("<Configure>", self._on_configure)

        if self._var is not None:
            self._var.trace_add("write", lambda *_: self._sync_from_var())

        self._redraw()

    # -- state ------------------------------------------------------------
    def get(self) -> float:
        return self._value

    def set(self, value: float) -> None:
        value = max(self._from, min(self._to, float(value)))
        if value == self._value:
            return
        self._value = value
        if self._var is not None and self._var.get() != value:
            self._var.set(value)
        self._redraw()
        if self._command is not None:
            self._command(self._value)

    def _sync_from_var(self):
        if self._var is None:
            return
        v = float(self._var.get())
        if v != self._value:
            self._value = max(self._from, min(self._to, v))
            self._redraw()

    # -- geometry ---------------------------------------------------------
    def _knob_radius(self) -> int:
        return 8

    def _value_to_x(self, v: float) -> float:
        r = self._knob_radius()
        usable = self._cw - 2 * r
        if self._to == self._from:
            return r
        return r + (v - self._from) / (self._to - self._from) * usable

    def _x_to_value(self, x: float) -> float:
        r = self._knob_radius()
        usable = self._cw - 2 * r
        if usable <= 0:
            return self._from
        t = (x - r) / usable
        t = max(0.0, min(1.0, t))
        return self._from + t * (self._to - self._from)

    # -- events -----------------------------------------------------------
    def _on_press(self, e):
        self._dragging = True
        self.set(self._x_to_value(e.x))

    def _on_drag(self, e):
        if self._dragging:
            self.set(self._x_to_value(e.x))

    def _on_release(self, _e):
        self._dragging = False
        self._redraw()

    def _on_enter(self, _e):
        self._hover = True
        self._redraw()

    def _on_leave(self, _e):
        self._hover = False
        self._redraw()

    def _on_configure(self, e):
        self._cw = e.width
        self._ch = e.height
        self._redraw()

    # -- drawing ----------------------------------------------------------
    def _redraw(self):
        p = self._palette
        self.delete("all")
        r = self._knob_radius()
        mid = self._ch / 2
        trough_h = 5
        x_left = r
        x_right = self._cw - r
        knob_x = self._value_to_x(self._value)

        # Trough background (un-filled portion).
        draw_rounded_rect(
            self, x_left, mid - trough_h / 2, x_right, mid + trough_h / 2,
            r=trough_h / 2, fill=p.button_bg_active, outline="",
        )
        # Filled portion from min to current.
        if knob_x > x_left:
            draw_rounded_rect(
                self, x_left, mid - trough_h / 2, knob_x, mid + trough_h / 2,
                r=trough_h / 2, fill=p.accent, outline="",
            )

        # Focus ring on hover — subtle accent halo around the knob.
        if self._hover or self._dragging:
            self.create_oval(
                knob_x - r - 3, mid - r - 3, knob_x + r + 3, mid + r + 3,
                outline=p.accent, width=0, fill=self._lighten(p.accent, 0.82),
            )

        # Knob: white with a 1px border so it stands out on any trough color.
        knob_border = p.strong_border if not p.dark else "#1a1a1a"
        self.create_oval(
            knob_x - r, mid - r, knob_x + r, mid + r,
            fill="#ffffff", outline=knob_border, width=1,
        )

    @staticmethod
    def _lighten(hex_color: str, amount: float) -> str:
        """Mix `hex_color` toward white by `amount` (0=same, 1=white)."""
        h = hex_color.lstrip("#")
        r, g, b = int(h[0:2], 16), int(h[2:4], 16), int(h[4:6], 16)
        r = int(r + (255 - r) * amount)
        g = int(g + (255 - g) * amount)
        b = int(b + (255 - b) * amount)
        return f"#{r:02x}{g:02x}{b:02x}"
