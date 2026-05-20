# =============================================================
#  views/driver/driver_portal.py — Driver dashboard
# =============================================================

import tkinter as tk
from tkinter import ttk, messagebox
import sys, os
sys.path.append(os.path.dirname(os.path.dirname(
    os.path.dirname(os.path.abspath(__file__)))))

import config
from modules.widgets  import (make_topbar, make_sidebar,
                               stat_card, make_tree,
                               section_title, section_subtitle)
from modules.driver   import (get_driver_by_user_id,
                               update_availability,
                               get_driver_earnings)
from modules.booking  import (get_driver_bookings,
                               driver_update_trip_status)


class DriverPortal(tk.Frame):

    def __init__(self, parent, app, user: dict):
        super().__init__(parent, bg=config.COLOR_BG)
        self.app    = app
        self.user   = user
        self.driver = get_driver_by_user_id(user["id"])

        if not self.driver:
            tk.Label(self, text="⚠️  Driver profile not found. Contact admin.",
                     font=config.FONT_HEADING,
                     bg=config.COLOR_BG, fg=config.COLOR_DANGER
                     ).pack(expand=True)
            return

        make_topbar(self,
                    title="Taxi Booking System — Driver Portal",
                    user_name=self.user["full_name"],
                    logout_cmd=self.app.logout,
                    role_color=config.COLOR_SUCCESS)

        body = tk.Frame(self, bg=config.COLOR_BG)
        body.pack(fill="both", expand=True)

        make_sidebar(body, [
            ("🏠  Dashboard",       self._tab_dashboard),
            ("📋  My Trips",        self._tab_my_trips),
            ("🚗  My Vehicle",      self._tab_vehicle),
            ("💰  Earnings",        self._tab_earnings),
        ])

        self.content = tk.Frame(body, bg=config.COLOR_BG)
        self.content.pack(side="right", fill="both", expand=True)

        self._tab_dashboard()

    def _clear(self):
        for w in self.content.winfo_children():
            w.destroy()

    # ── Dashboard ─────────────────────────────────────────────

    def _tab_dashboard(self):
        self._clear()
        d = self.driver
        section_title(self.content,
                      f"Welcome, {self.user['full_name'].split()[0]}! 🚗")
        section_subtitle(self.content, "Driver dashboard overview")

        # Availability toggle
        avail_card = tk.Frame(self.content, bg=config.COLOR_WHITE,
                              padx=20, pady=14)
        avail_card.pack(padx=20, pady=(4, 10), fill="x")

        cur_color = {
            "Available": config.COLOR_SUCCESS,
            "On Trip":   config.COLOR_WARNING,
            "Offline":   config.COLOR_TEXT_LIGHT,
        }.get(d["availability"], config.COLOR_TEXT_LIGHT)

        tk.Label(avail_card,
                 text=f"Current Status:  ● {d['availability']}",
                 font=config.FONT_SUBHEAD,
                 bg=config.COLOR_WHITE, fg=cur_color
                 ).pack(side="left")

        btn_frame = tk.Frame(avail_card, bg=config.COLOR_WHITE)
        btn_frame.pack(side="right")

        for status, color in [("Available", config.COLOR_SUCCESS),
                               ("Offline",   config.COLOR_TEXT_LIGHT)]:
            tk.Button(btn_frame, text=status,
                      font=config.FONT_SMALL,
                      bg=color, fg="white",
                      relief="flat", cursor="hand2", padx=10,
                      command=lambda s=status: self._set_avail(s)
                      ).pack(side="left", padx=4)

        # Stat cards
        earnings = get_driver_earnings(d["id"])
        bookings = get_driver_bookings(d["id"])
        confirmed = sum(1 for b in bookings if b["status"] == "Confirmed")

        cards = tk.Frame(self.content, bg=config.COLOR_BG)
        cards.pack(padx=20, pady=4, anchor="w")
        stat_card(cards, "Total Trips",     d["total_trips"],
                  config.COLOR_INFO,    0)
        stat_card(cards, "Active Trips",    confirmed,
                  config.COLOR_WARNING, 1)
        stat_card(cards, "Rating",          f"{float(d['rating']):.1f} ⭐",
                  config.COLOR_SECONDARY if True else "",  2)
        stat_card(cards, "Earned (NPR)",
                  f"{earnings['total_earned']:.0f}",
                  config.COLOR_SUCCESS, 3)

        # Vehicle info strip
        section_title(self.content, "My Vehicle")
        vcard = tk.Frame(self.content, bg=config.COLOR_WHITE,
                         padx=20, pady=12)
        vcard.pack(padx=20, pady=(0, 8), fill="x")

        for label, val in [
            ("Type",    d["vehicle_type"]),
            ("Number",  d["vehicle_number"]),
            ("Model",   d["vehicle_model"]),
            ("License", d["license_number"]),
        ]:
            row = tk.Frame(vcard, bg=config.COLOR_WHITE)
            row.pack(anchor="w", pady=2)
            tk.Label(row, text=f"{label}:",
                     font=("Helvetica", 10, "bold"),
                     bg=config.COLOR_WHITE,
                     fg=config.COLOR_TEXT_DARK,
                     width=10, anchor="w").pack(side="left")
            tk.Label(row, text=val,
                     font=config.FONT_NORMAL,
                     bg=config.COLOR_WHITE,
                     fg=config.COLOR_TEXT_LIGHT).pack(side="left")

    def _set_avail(self, status: str):
        ok, msg = update_availability(self.driver["id"], status)
        if ok:
            self.driver["availability"] = status
            messagebox.showinfo("Updated", msg)
            self._tab_dashboard()
        else:
            messagebox.showerror("Error", msg)

    # ── My Trips ──────────────────────────────────────────────

    def _tab_my_trips(self):
        self._clear()
        section_title(self.content, "My Assigned Trips 📋")
        section_subtitle(self.content,
                         "Confirmed trips are yours to complete")

        cols   = ("ID","Customer","Phone","Pickup","Dropoff",
                  "Vehicle","Date","Time","Fare","Status")
        widths = (40, 110, 100, 120, 120, 65, 90, 70, 80, 85)
        self.trip_tree, _ = make_tree(self.content, cols,
                                      widths, height=15)

        bookings = get_driver_bookings(self.driver["id"])
        for b in bookings:
            self.trip_tree.insert(
                "", "end",
                values=(b["id"],
                        b.get("customer_name", ""),
                        b.get("customer_phone", ""),
                        b["pickup_location"],
                        b["dropoff_location"],
                        b["vehicle_type"],
                        str(b["booking_date"]),
                        str(b.get("booking_time", "")),
                        f"NPR {b['fare']:.2f}",
                        b["status"]),
                tags=(b["status"],)
            )

        ctrl = tk.Frame(self.content, bg=config.COLOR_BG)
        ctrl.pack(anchor="w", padx=20, pady=8)

        tk.Button(ctrl, text="✅  Mark as Completed",
                  font=config.FONT_BUTTON,
                  bg=config.COLOR_SUCCESS, fg="white",
                  relief="flat", cursor="hand2",
                  padx=12, pady=4,
                  command=self._complete_trip
                  ).pack(side="left", padx=(0, 8))

        tk.Button(ctrl, text="🔄  Refresh",
                  font=config.FONT_BUTTON,
                  bg=config.COLOR_INFO, fg="white",
                  relief="flat", cursor="hand2",
                  padx=12, pady=4,
                  command=self._tab_my_trips
                  ).pack(side="left")

    def _complete_trip(self):
        sel = self.trip_tree.selection()
        if not sel:
            messagebox.showinfo("No Selection",
                                "Select a trip to mark as completed.")
            return
        bid = int(self.trip_tree.item(sel[0], "values")[0])
        ok, msg = driver_update_trip_status(bid, self.driver["id"],
                                             "Completed")
        if ok:
            messagebox.showinfo("Done", msg)
            self._tab_my_trips()
        else:
            messagebox.showerror("Error", msg)

    # ── Vehicle info ──────────────────────────────────────────

    def _tab_vehicle(self):
        self._clear()
        d = self.driver
        section_title(self.content, "My Vehicle 🚗")

        card = tk.Frame(self.content, bg=config.COLOR_WHITE,
                        padx=36, pady=28)
        card.pack(padx=20, pady=10, anchor="nw")

        details = [
            ("Vehicle Type",    d["vehicle_type"]),
            ("Vehicle Number",  d["vehicle_number"]),
            ("Vehicle Model",   d["vehicle_model"]),
            ("License Number",  d["license_number"]),
            ("Availability",    d["availability"]),
            ("Total Trips",     str(d["total_trips"])),
            ("Rating",          f"{float(d['rating']):.2f} / 5.00"),
        ]
        for i, (lbl, val) in enumerate(details):
            tk.Label(card, text=f"{lbl}:",
                     font=("Helvetica", 10, "bold"),
                     bg=config.COLOR_WHITE,
                     fg=config.COLOR_TEXT_DARK,
                     width=16, anchor="w"
                     ).grid(row=i, column=0, sticky="w", pady=7)
            tk.Label(card, text=val,
                     font=config.FONT_NORMAL,
                     bg=config.COLOR_WHITE,
                     fg=config.COLOR_TEXT_LIGHT
                     ).grid(row=i, column=1, sticky="w", padx=12)

        tk.Label(card,
                 text="To update vehicle details, contact your admin.",
                 font=config.FONT_SMALL,
                 bg=config.COLOR_WHITE,
                 fg=config.COLOR_DANGER
                 ).grid(row=len(details), column=0,
                        columnspan=2, pady=(16, 0), sticky="w")

    # ── Earnings ──────────────────────────────────────────────

    def _tab_earnings(self):
        self._clear()
        section_title(self.content, "My Earnings 💰")
        section_subtitle(self.content, "Based on completed trips only")

        e = get_driver_earnings(self.driver["id"])

        card = tk.Frame(self.content, bg=config.COLOR_WHITE,
                        padx=36, pady=28)
        card.pack(padx=20, pady=10, anchor="nw")

        for lbl, val in [
            ("Total Completed Trips", str(e["total_trips"])),
            ("Total Earned",          f"NPR {e['total_earned']:,.2f}"),
            ("Average per Trip",
             f"NPR {(e['total_earned']/e['total_trips']):.2f}"
             if e["total_trips"] > 0 else "NPR 0.00"),
        ]:
            row = tk.Frame(card, bg=config.COLOR_WHITE)
            row.pack(anchor="w", pady=6)
            tk.Label(row, text=f"{lbl}:",
                     font=("Helvetica", 11, "bold"),
                     bg=config.COLOR_WHITE,
                     fg=config.COLOR_TEXT_DARK,
                     width=24, anchor="w").pack(side="left")
            tk.Label(row, text=val,
                     font=("Helvetica", 14, "bold"),
                     bg=config.COLOR_WHITE,
                     fg=config.COLOR_SUCCESS).pack(side="left")
