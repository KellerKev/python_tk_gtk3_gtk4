"""Tkinter skin that mimics GTK3 (Adwaita) and GTK4 (libadwaita)."""

from .theme import Palette, GTK3_LIGHT, GTK3_DARK, GTK4_LIGHT, GTK4_DARK, apply_skin
from .widgets import (
    Avatar, Check, HeaderBar, ListBox, ListRow, PillButton, Radio, Scale,
    Separator, Switch,
)

__all__ = [
    "Palette",
    "GTK3_LIGHT",
    "GTK3_DARK",
    "GTK4_LIGHT",
    "GTK4_DARK",
    "apply_skin",
    "Avatar",
    "Check",
    "HeaderBar",
    "ListBox",
    "ListRow",
    "PillButton",
    "Radio",
    "Scale",
    "Separator",
    "Switch",
]
