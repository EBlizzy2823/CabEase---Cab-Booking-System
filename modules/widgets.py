# =============================================================
#  modules/widgets.py — Reusable Tkinter widget factories
# =============================================================

import tkinter as tk
from tkinter import ttk
import sys, os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import config


# ── Top navigation bar ────────────────────────────────────────

def make_topbar(parent, title: str, user_name: str,
                logout_cmd, role_color: str = None) -> tk.Frame:
    color = role_color or config.COLOR_PRIMARY
    bar = tk.Frame(parent, bg=color, height=58)
    bar.pack(fill="x")
    bar.pack_propagate(False)

    tk.Label(bar, text=f"🚖  {title}",
             font=("Helvetica", 14, "bold"),
             bg=color, fg=config.COLOR_SECONDARY
             ).pack(side="left", padx=18)

    tk.Button(bar, text="⏻  Logout",
              font=config.FONT_SMALL,
              bg=config.COLOR_DANGER, fg="white",
              relief="flat", cursor="hand2", padx=10,
              command=logout_cmd
              ).pack(side="right", padx=14, pady=10)

    tk.Label(bar, text=f"👤  {user_name}",
             font=config.FONT_LABEL,
             bg=color, fg="white"
             ).pack(side="right", padx=4)

    return bar


# ── Sidebar ───────────────────────────────────────────────────

def make_sidebar(parent, items: list[tuple[str, callable]],
                 width: int = 200) -> tk.Frame:
    """
    items: list of (label, command) tuples.
    Returns the sidebar Frame.
    """
    sb = tk.Frame(parent, bg=config.COLOR_SIDEBAR, width=width)
    sb.pack(side="left", fill="y")
    sb.pack_propagate(False)

    # Spacer at top
    tk.Label(sb, bg=config.COLOR_SIDEBAR, height=1).pack()

    for label, cmd in items:
        btn = tk.Button(sb, text=f"  {label}",
                        font=config.FONT_LABEL,
                        bg=config.COLOR_SIDEBAR, fg="white",
                        activebackground=config.COLOR_SECONDARY,
                        activeforeground=config.COLOR_PRIMARY,
                        relief="flat", anchor="w",
                        cursor="hand2", width=24, height=2,
                        command=cmd)
        btn.pack(fill="x", pady=1)

    return sb


# ── Stat card ─────────────────────────────────────────────────

def stat_card(parent, title: str, value: str,
              color: str, col: int):
    card = tk.Frame(parent, bg=color, width=155, height=90)
    card.grid(row=0, column=col, padx=6, pady=4)
    card.pack_propagate(False)

    tk.Label(card, text=str(value),
             font=("Helvetica", 20, "bold"),
             bg=color, fg="white").pack(pady=(14, 0))
    tk.Label(card, text=title,
             font=config.FONT_SMALL,
             bg=color, fg="white").pack()


# ── Standard Treeview builder ─────────────────────────────────

def make_tree(parent, columns: list[str],
              col_widths: list[int],
              height: int = 14) -> tuple[ttk.Treeview, ttk.Scrollbar]:
    frame = tk.Frame(parent, bg=config.COLOR_BG)
    frame.pack(fill="both", expand=True, padx=4)

    tree = ttk.Treeview(frame, columns=columns,
                         show="headings", height=height)
    for col, w in zip(columns, col_widths):
        tree.heading(col, text=col)
        tree.column(col, width=w, anchor="center")

    # Status colour tags
    tree.tag_configure("Pending",   background="#FEF9E7")
    tree.tag_configure("Confirmed", background="#EBF5FB")
    tree.tag_configure("Completed", background="#EAFAF1")
    tree.tag_configure("Cancelled", background="#FDEDEC")
    tree.tag_configure("Available", background="#EAFAF1")
    tree.tag_configure("On Trip",   background="#EBF5FB")
    tree.tag_configure("Offline",   background="#F2F3F4")

    scroll = ttk.Scrollbar(frame, orient="vertical",
                           command=tree.yview)
    tree.configure(yscrollcommand=scroll.set)
    tree.pack(side="left", fill="both", expand=True)
    scroll.pack(side="left", fill="y")

    return tree, scroll


# ── Section heading ───────────────────────────────────────────

def section_title(parent, text: str):
    tk.Label(parent, text=text,
             font=config.FONT_HEADING,
             bg=config.COLOR_BG,
             fg=config.COLOR_TEXT_DARK
             ).pack(anchor="w", padx=20, pady=(16, 2))

def section_subtitle(parent, text: str):
    tk.Label(parent, text=text,
             font=config.FONT_SMALL,
             bg=config.COLOR_BG,
             fg=config.COLOR_TEXT_LIGHT
             ).pack(anchor="w", padx=20, pady=(0, 10))


# ── Form helpers ──────────────────────────────────────────────

def form_label(parent, text: str, row: int, bg=None):
    bg = bg or config.COLOR_WHITE
    tk.Label(parent, text=text, font=config.FONT_LABEL,
             bg=bg, fg=config.COLOR_TEXT_DARK, anchor="w"
             ).grid(row=row, column=0, sticky="w",
                    padx=(0, 10), pady=(6, 1))

def form_entry(parent, var: tk.StringVar,
               row: int, show: str = "",
               width: int = 28) -> tk.Entry:
    e = tk.Entry(parent, textvariable=var,
                 font=config.FONT_NORMAL,
                 width=width, relief="solid", bd=1, show=show)
    e.grid(row=row, column=0, ipady=5, pady=(0, 2), sticky="ew")
    return e
