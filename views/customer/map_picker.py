# =============================================================
#  views/customer/map_picker.py
#  Location picker popup — search by name with live suggestions
#  No external browser, no CDN, works 100% reliably.
# =============================================================

import tkinter as tk
from tkinter import ttk, messagebox
import threading
import sys, os
sys.path.append(os.path.dirname(os.path.dirname(
    os.path.dirname(os.path.abspath(__file__)))))

import config
from modules.map_utils import geocode_place, reverse_geocode, search_places


class MapPickerWindow(tk.Toplevel):
    """
    A popup that lets the customer search for a location by name.
    Shows live suggestions as they type, then confirms the selection.
    Calls on_location_selected(place_name, lat, lng) on confirm.
    """

    def __init__(self, parent, title: str,
                 on_location_selected: callable):
        super().__init__(parent)
        self.title(f"📍 Select Location — {title}")
        self.geometry("560x480")
        self.resizable(False, False)
        self.configure(bg=config.COLOR_BG)
        self.transient(parent)
        self.grab_set()

        self.on_location_selected = on_location_selected
        self._selected_lat  = None
        self._selected_lng  = None
        self._selected_name = None
        self._search_thread = None

        # Centre on parent
        self.update_idletasks()
        px = parent.winfo_rootx()
        py = parent.winfo_rooty()
        pw = parent.winfo_width()
        ph = parent.winfo_height()
        x  = px + (pw - 560) // 2
        y  = py + (ph - 480) // 2
        self.geometry(f"+{x}+{y}")

        self._build()

    # ── UI ────────────────────────────────────────────────────

    def _build(self):
        # Header
        header = tk.Frame(self, bg=config.COLOR_PRIMARY, height=52)
        header.pack(fill="x")
        header.pack_propagate(False)
        tk.Label(header, text="📍  Search for a Location in Nepal",
                 font=("Helvetica", 12, "bold"),
                 bg=config.COLOR_PRIMARY, fg="white"
                 ).pack(side="left", padx=16, pady=14)

        # Search bar
        search_frame = tk.Frame(self, bg=config.COLOR_BG, pady=14)
        search_frame.pack(fill="x", padx=20)

        tk.Label(search_frame, text="Type a place name:",
                 font=config.FONT_LABEL,
                 bg=config.COLOR_BG,
                 fg=config.COLOR_TEXT_DARK
                 ).pack(anchor="w", pady=(0, 4))

        entry_row = tk.Frame(search_frame, bg=config.COLOR_BG)
        entry_row.pack(fill="x")

        self.search_var = tk.StringVar()
        self.search_entry = tk.Entry(entry_row,
                                     textvariable=self.search_var,
                                     font=("Helvetica", 13),
                                     relief="solid", bd=1)
        self.search_entry.pack(side="left", fill="x",
                               expand=True, ipady=7, padx=(0, 8))

        tk.Button(entry_row, text="🔍  Search",
                  font=config.FONT_BUTTON,
                  bg=config.COLOR_SECONDARY,
                  fg=config.COLOR_PRIMARY,
                  relief="flat", cursor="hand2",
                  padx=12, pady=4,
                  command=self._do_search
                  ).pack(side="left")

        # Hint
        tk.Label(search_frame,
                 text="e.g.  Thamel Kathmandu,  Patan Durbar Square,  Kirtipur",
                 font=config.FONT_SMALL,
                 bg=config.COLOR_BG, fg=config.COLOR_TEXT_LIGHT
                 ).pack(anchor="w", pady=(4, 0))

        # Status label
        self.status_var = tk.StringVar(
            value="Type a location name and press Search."
        )
        tk.Label(self, textvariable=self.status_var,
                 font=config.FONT_SMALL,
                 bg=config.COLOR_BG, fg=config.COLOR_TEXT_LIGHT
                 ).pack(anchor="w", padx=20, pady=(0, 4))

        # Results list
        list_frame = tk.Frame(self, bg=config.COLOR_BG)
        list_frame.pack(fill="both", expand=True, padx=20)

        tk.Label(list_frame, text="Results  (double-click to select):",
                 font=config.FONT_LABEL,
                 bg=config.COLOR_BG,
                 fg=config.COLOR_TEXT_DARK
                 ).pack(anchor="w", pady=(0, 4))

        lb_frame = tk.Frame(list_frame, bg=config.COLOR_BG)
        lb_frame.pack(fill="both", expand=True)

        scrollbar = ttk.Scrollbar(lb_frame)
        scrollbar.pack(side="right", fill="y")

        self.results_lb = tk.Listbox(lb_frame,
                                      font=config.FONT_NORMAL,
                                      relief="solid", bd=1,
                                      selectmode="single",
                                      activestyle="dotbox",
                                      yscrollcommand=scrollbar.set,
                                      height=10)
        self.results_lb.pack(side="left", fill="both", expand=True)
        scrollbar.config(command=self.results_lb.yview)

        self.results_lb.bind("<Double-Button-1>",
                             lambda e: self._select_result())
        self.results_lb.bind("<Return>",
                             lambda e: self._select_result())

        # Store raw result data alongside listbox entries
        self._results_data = []   # list of (display_name, lat, lng)

        # Selected preview
        self.preview_frame = tk.Frame(self, bg="#EAFAF1",
                                       padx=14, pady=10)
        self.preview_lbl = tk.Label(self.preview_frame,
                                     text="",
                                     font=config.FONT_LABEL,
                                     bg="#EAFAF1",
                                     fg=config.COLOR_SUCCESS,
                                     wraplength=440,
                                     justify="left")
        self.preview_lbl.pack(anchor="w")

        # Bottom buttons
        btn_frame = tk.Frame(self, bg=config.COLOR_BG, pady=12)
        btn_frame.pack(fill="x", padx=20)

        self.confirm_btn = tk.Button(btn_frame,
                                      text="✓  Use Selected Location",
                                      font=config.FONT_BUTTON,
                                      bg=config.COLOR_SUCCESS,
                                      fg="white",
                                      relief="flat", cursor="hand2",
                                      padx=14, pady=6,
                                      state="disabled",
                                      command=self._confirm)
        self.confirm_btn.pack(side="left", padx=(0, 10))

        tk.Button(btn_frame, text="Cancel",
                  font=config.FONT_BUTTON,
                  bg=config.COLOR_DANGER, fg="white",
                  relief="flat", cursor="hand2",
                  padx=14, pady=6,
                  command=self.destroy
                  ).pack(side="left")

        # Bind Enter key to search
        self.search_entry.bind("<Return>", lambda e: self._do_search())
        self.search_entry.focus_set()

    # ── Search ────────────────────────────────────────────────

    def _do_search(self):
        query = self.search_var.get().strip()
        if not query:
            messagebox.showwarning("Empty", "Please enter a place name.",
                                   parent=self)
            return

        self.status_var.set("🔍  Searching…")
        self.results_lb.delete(0, "end")
        self._results_data = []
        self._hide_preview()
        self.confirm_btn.config(state="disabled")
        self.update()

        def run():
            results = search_places(query)
            self.after(0, lambda: self._show_results(results))

        threading.Thread(target=run, daemon=True).start()

    def _show_results(self, results: list[dict]):
        self.results_lb.delete(0, "end")
        self._results_data = []

        if not results:
            self.status_var.set(
                "No results found. Try a different name "
                "(e.g. add 'Kathmandu' at the end)."
            )
            return

        self.status_var.set(
            f"Found {len(results)} result(s). Double-click one to select."
        )

        for r in results:
            # Short display: first 2 meaningful parts of address
            short = self._shorten(r["display_name"])
            self.results_lb.insert("end", short)
            self._results_data.append(
                (short, float(r["lat"]), float(r["lon"]))
            )

    def _shorten(self, display_name: str) -> str:
        """Trims Nominatim's long display name to something readable."""
        parts = [p.strip() for p in display_name.split(",")]
        # Keep up to 4 parts
        return ", ".join(parts[:4])

    # ── Selection ─────────────────────────────────────────────

    def _select_result(self):
        sel = self.results_lb.curselection()
        if not sel:
            return
        idx  = sel[0]
        name, lat, lng = self._results_data[idx]
        self._selected_name = name
        self._selected_lat  = lat
        self._selected_lng  = lng

        # Show preview
        self.preview_lbl.config(
            text=f"✅  Selected:  {name}\n"
                 f"    Coordinates: {lat:.5f}, {lng:.5f}"
        )
        self.preview_frame.pack(fill="x", padx=20, pady=(0, 4))
        self.confirm_btn.config(state="normal")

    def _hide_preview(self):
        self.preview_frame.pack_forget()

    # ── Confirm ───────────────────────────────────────────────

    def _confirm(self):
        if self._selected_name:
            self.on_location_selected(
                self._selected_name,
                self._selected_lat,
                self._selected_lng
            )
            self.destroy()
