# =============================================================
#  views/admin/admin_portal.py — Admin dashboard
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
from modules.booking  import (get_all_bookings, get_dashboard_stats,
                               assign_driver, admin_update_booking_status)
from modules.driver   import (get_all_drivers, get_available_drivers,
                               admin_delete_driver, admin_update_driver)
from modules.auth     import get_user_by_id
from database.db_connection import execute_query


class AdminPortal(tk.Frame):

    def __init__(self, parent, app, user: dict):
        super().__init__(parent, bg=config.COLOR_BG)
        self.app  = app
        self.user = user

        make_topbar(self,
                    title="Taxi Booking System — Admin Panel",
                    user_name=self.user["full_name"],
                    logout_cmd=self.app.logout,
                    role_color=config.COLOR_DANGER)

        body = tk.Frame(self, bg=config.COLOR_BG)
        body.pack(fill="both", expand=True)

        make_sidebar(body, [
            ("🏠  Dashboard",       self._tab_dashboard),
            ("📋  All Bookings",    self._tab_bookings),
            ("🚗  Manage Drivers",  self._tab_drivers),
            ("👥  Manage Customers",self._tab_customers),
            ("💰  Revenue",         self._tab_revenue),
            ("📊  Fare Rates",      self._tab_fares),
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
        section_title(self.content, "Admin Dashboard 🛡️")
        section_subtitle(self.content, "System-wide overview")

        stats = get_dashboard_stats()

        cards = tk.Frame(self.content, bg=config.COLOR_BG)
        cards.pack(padx=20, pady=4, anchor="w")

        card_data = [
            ("Total Bookings",  stats["total_bookings"],  config.COLOR_INFO),
            ("Pending",         stats["pending"],          config.COLOR_WARNING),
            ("Confirmed",       stats["confirmed"],        "#8E44AD"),
            ("Completed",       stats["completed"],        config.COLOR_SUCCESS),
            ("Customers",       stats["total_customers"], config.COLOR_PRIMARY),
            ("Drivers",         stats["total_drivers"],   config.COLOR_ACCENT),
        ]
        for i, (title, val, color) in enumerate(card_data):
            stat_card(cards, title, val, color, i)

        # Revenue highlight
        rev_frame = tk.Frame(self.content, bg=config.COLOR_SUCCESS,
                             padx=20, pady=12)
        rev_frame.pack(padx=20, pady=(8, 4), fill="x")
        tk.Label(rev_frame,
                 text=f"💰  Total Revenue (Completed Trips):   "
                      f"NPR {stats['revenue']:,.2f}",
                 font=config.FONT_SUBHEAD,
                 bg=config.COLOR_SUCCESS, fg="white"
                 ).pack(anchor="w")

        # Recent bookings
        section_title(self.content, "Recent Bookings")
        cols   = ("ID","Customer","Driver","Pickup","Dropoff",
                  "Vehicle","Date","Fare","Status")
        widths = (40,110,110,120,120,65,90,80,80)
        tree, _ = make_tree(self.content, cols, widths, height=8)
        for b in get_all_bookings()[:10]:
            driver = b.get("driver_name") or "—"
            tree.insert("", "end",
                        values=(b["id"],
                                b["customer_name"], driver,
                                b["pickup_location"],
                                b["dropoff_location"],
                                b["vehicle_type"],
                                str(b["booking_date"]),
                                f"NPR {b['fare']:.2f}",
                                b["status"]),
                        tags=(b["status"],))

    # ── All Bookings ──────────────────────────────────────────

    def _tab_bookings(self):
        self._clear()
        section_title(self.content, "All Bookings 📋")
        section_subtitle(self.content,
                         "Assign drivers, change statuses, manage trips")

        cols   = ("ID","Customer","Driver","Pickup","Dropoff",
                  "Vehicle","Date","Fare","Status")
        widths = (40,110,110,130,130,65,95,80,80)
        self.book_tree, _ = make_tree(self.content, cols,
                                      widths, height=13)
        self._load_bookings()

        ctrl = tk.Frame(self.content, bg=config.COLOR_BG)
        ctrl.pack(anchor="w", padx=20, pady=8)

        # Status change controls
        tk.Label(ctrl, text="Change status:",
                 font=config.FONT_LABEL,
                 bg=config.COLOR_BG).pack(side="left")

        self.status_var = tk.StringVar(value="Confirmed")
        for s in config.BOOKING_STATUSES:
            tk.Radiobutton(ctrl, text=s,
                           variable=self.status_var, value=s,
                           font=config.FONT_SMALL,
                           bg=config.COLOR_BG
                           ).pack(side="left", padx=5)

        tk.Button(ctrl, text="Apply Status",
                  font=config.FONT_BUTTON,
                  bg=config.COLOR_PRIMARY, fg="white",
                  relief="flat", cursor="hand2", padx=10,
                  command=self._apply_status
                  ).pack(side="left", padx=10)

        # Assign driver section
        assign_frame = tk.Frame(self.content, bg=config.COLOR_WHITE,
                                padx=20, pady=10)
        assign_frame.pack(padx=20, pady=(0, 8), fill="x")

        tk.Label(assign_frame, text="Assign Driver to Selected Booking:",
                 font=("Helvetica", 10, "bold"),
                 bg=config.COLOR_WHITE,
                 fg=config.COLOR_TEXT_DARK).pack(side="left")

        # Dropdown of available drivers
        drivers = get_available_drivers()
        driver_names = [f"{d['id']} — {d['full_name']} "
                        f"({d['vehicle_type']}, {d['vehicle_number']})"
                        for d in drivers]

        self.driver_var = tk.StringVar()
        self.driver_cb = ttk.Combobox(assign_frame,
                                       textvariable=self.driver_var,
                                       values=driver_names,
                                       state="readonly", width=42,
                                       font=config.FONT_LABEL)
        self.driver_cb.pack(side="left", padx=10)

        tk.Button(assign_frame, text="Assign",
                  font=config.FONT_BUTTON,
                  bg=config.COLOR_SECONDARY,
                  fg=config.COLOR_PRIMARY,
                  relief="flat", cursor="hand2", padx=10,
                  command=self._assign_driver
                  ).pack(side="left")

    def _load_bookings(self):
        for row in self.book_tree.get_children():
            self.book_tree.delete(row)
        for b in get_all_bookings():
            driver = b.get("driver_name") or "Not Assigned"
            self.book_tree.insert(
                "", "end",
                values=(b["id"],
                        b["customer_name"], driver,
                        b["pickup_location"],
                        b["dropoff_location"],
                        b["vehicle_type"],
                        str(b["booking_date"]),
                        f"NPR {b['fare']:.2f}",
                        b["status"]),
                tags=(b["status"],)
            )

    def _apply_status(self):
        sel = self.book_tree.selection()
        if not sel:
            messagebox.showinfo("No selection",
                                "Please select a booking.")
            return
        bid = int(self.book_tree.item(sel[0], "values")[0])
        ok, msg = admin_update_booking_status(bid, self.status_var.get())
        if ok:
            messagebox.showinfo("Updated", msg)
            self._load_bookings()
        else:
            messagebox.showerror("Error", msg)

    def _assign_driver(self):
        sel = self.book_tree.selection()
        if not sel:
            messagebox.showinfo("No selection",
                                "Please select a booking first.")
            return
        if not self.driver_var.get():
            messagebox.showinfo("No driver",
                                "Please select a driver to assign.")
            return
        bid      = int(self.book_tree.item(sel[0], "values")[0])
        driver_id = int(self.driver_var.get().split("—")[0].strip())
        ok, msg   = assign_driver(bid, driver_id)
        if ok:
            messagebox.showinfo("Assigned", msg)
            self._tab_bookings()
        else:
            messagebox.showerror("Error", msg)

    # ── Manage Drivers ────────────────────────────────────────

    def _tab_drivers(self):
        self._clear()
        section_title(self.content, "Manage Drivers 🚗")
        section_subtitle(self.content,
                         "View all registered drivers and their status")

        cols   = ("ID","Name","Email","Phone","License",
                  "Vehicle Type","Vehicle No.","Model",
                  "Availability","Trips","Rating")
        widths = (35,110,140,95,100,80,90,100,75,45,50)
        self.drv_tree, _ = make_tree(self.content, cols,
                                     widths, height=14)
        self._load_drivers()

        ctrl = tk.Frame(self.content, bg=config.COLOR_BG)
        ctrl.pack(anchor="w", padx=20, pady=8)

        tk.Button(ctrl, text="🗑️  Delete Driver",
                  font=config.FONT_BUTTON,
                  bg=config.COLOR_DANGER, fg="white",
                  relief="flat", cursor="hand2", padx=10, pady=4,
                  command=self._delete_driver
                  ).pack(side="left", padx=(0, 8))

        tk.Button(ctrl, text="🔄  Refresh",
                  font=config.FONT_BUTTON,
                  bg=config.COLOR_INFO, fg="white",
                  relief="flat", cursor="hand2", padx=10, pady=4,
                  command=self._tab_drivers
                  ).pack(side="left")

    def _load_drivers(self):
        for row in self.drv_tree.get_children():
            self.drv_tree.delete(row)
        for d in get_all_drivers():
            self.drv_tree.insert(
                "", "end",
                values=(d["id"], d["full_name"],
                        d["email"], d["phone"],
                        d["license_number"],
                        d["vehicle_type"],
                        d["vehicle_number"],
                        d["vehicle_model"],
                        d["availability"],
                        d["total_trips"],
                        f"{float(d['rating']):.2f}"),
                tags=(d["availability"],)
            )

    def _delete_driver(self):
        sel = self.drv_tree.selection()
        if not sel:
            messagebox.showinfo("No selection",
                                "Please select a driver.")
            return
        vals     = self.drv_tree.item(sel[0], "values")
        driver_id = int(vals[0])
        name      = vals[1]

        # Get user_id from driver_id
        rows = execute_query(
            "SELECT user_id FROM drivers WHERE id=%s",
            (driver_id,), fetch=True
        )
        if not rows:
            return
        user_id = rows[0]["user_id"]

        if messagebox.askyesno(
                "Confirm Delete",
                f"Delete driver '{name}' and all their records?"):
            ok, msg = admin_delete_driver(user_id)
            if ok:
                messagebox.showinfo("Deleted", msg)
                self._tab_drivers()
            else:
                messagebox.showerror("Error", msg)

    # ── Manage Customers ──────────────────────────────────────

    def _tab_customers(self):
        self._clear()
        section_title(self.content, "Manage Customers 👥")
        section_subtitle(self.content,
                         "All registered customer accounts")

        cols   = ("ID","Full Name","Email","Phone","Joined")
        widths = (40, 160, 200, 120, 150)
        self.cust_tree, _ = make_tree(self.content, cols,
                                      widths, height=16)

        customers = execute_query(
            """SELECT id, full_name, email, phone, created_at
                 FROM users WHERE role='customer'
                ORDER BY created_at DESC""",
            fetch=True
        ) or []

        for c in customers:
            self.cust_tree.insert(
                "", "end",
                values=(c["id"], c["full_name"],
                        c["email"], c["phone"],
                        str(c["created_at"]))
            )

        tk.Button(self.content, text="🗑️  Delete Customer",
                  font=config.FONT_BUTTON,
                  bg=config.COLOR_DANGER, fg="white",
                  relief="flat", cursor="hand2",
                  padx=10, pady=4,
                  command=self._delete_customer
                  ).pack(anchor="w", padx=20, pady=8)

    def _delete_customer(self):
        sel = self.cust_tree.selection()
        if not sel:
            messagebox.showinfo("No selection",
                                "Please select a customer.")
            return
        uid  = int(self.cust_tree.item(sel[0], "values")[0])
        name = self.cust_tree.item(sel[0], "values")[1]

        if messagebox.askyesno(
                "Confirm Delete",
                f"Delete customer '{name}' and all their bookings?"):
            execute_query(
                "DELETE FROM users WHERE id=%s AND role='customer'",
                (uid,)
            )
            messagebox.showinfo("Deleted",
                                f"Customer '{name}' deleted.")
            self._tab_customers()

    # ── Revenue ───────────────────────────────────────────────

    def _tab_revenue(self):
        self._clear()
        section_title(self.content, "Revenue Report 💰")
        section_subtitle(self.content,
                         "Earnings breakdown from completed trips")

        rows = execute_query(
            """SELECT vehicle_type,
                      COUNT(*)   AS total_bookings,
                      SUM(fare)  AS total_revenue
                 FROM bookings
                WHERE status='Completed'
                GROUP BY vehicle_type""",
            fetch=True
        ) or []

        cols   = ("Vehicle Type", "Completed Trips", "Total Revenue (NPR)")
        widths = (150, 150, 200)
        tree, _ = make_tree(self.content, cols, widths, height=6)
        grand_total = 0.0
        for r in rows:
            rev = float(r["total_revenue"] or 0)
            grand_total += rev
            tree.insert("", "end",
                        values=(r["vehicle_type"],
                                r["total_bookings"],
                                f"NPR {rev:,.2f}"))

        # Grand total row
        tree.insert("", "end",
                    values=("── TOTAL ──", "", f"NPR {grand_total:,.2f}"))

        # Per-driver earnings
        section_title(self.content, "Per-Driver Earnings")
        drv_rows = execute_query(
            """SELECT u.full_name, d.vehicle_type,
                      COUNT(b.id) AS trips,
                      SUM(b.fare) AS earned
                 FROM bookings b
                 JOIN drivers d ON b.driver_id = d.id
                 JOIN users   u ON d.user_id   = u.id
                WHERE b.status = 'Completed'
                GROUP BY d.id
                ORDER BY earned DESC""",
            fetch=True
        ) or []

        cols2  = ("Driver", "Vehicle Type", "Completed Trips", "Earned (NPR)")
        widths2 = (160, 120, 130, 160)
        tree2, _ = make_tree(self.content, cols2, widths2, height=8)
        for r in drv_rows:
            tree2.insert("", "end",
                         values=(r["full_name"],
                                 r["vehicle_type"],
                                 r["trips"],
                                 f"NPR {float(r['earned'] or 0):,.2f}"))

    # ── Fare Rates ────────────────────────────────────────────

    def _tab_fares(self):
        self._clear()
        section_title(self.content, "Fare Rate Management 📊")
        section_subtitle(self.content,
                         "Current fare structure (editable in DB)")

        rates = execute_query(
            "SELECT * FROM fare_rates ORDER BY base_fare",
            fetch=True
        ) or []

        cols   = ("Vehicle Type", "Base Fare (NPR)", "Per KM Rate (NPR)",
                  "Example: 10 km Fare")
        widths = (150, 150, 150, 180)
        tree, _ = make_tree(self.content, cols, widths, height=5)

        for r in rates:
            base = float(r["base_fare"])
            rate = float(r["per_km_rate"])
            tree.insert("", "end",
                        values=(r["vehicle_type"],
                                f"NPR {base:.2f}",
                                f"NPR {rate:.2f}",
                                f"NPR {base + rate*10:.2f}"))

        tk.Label(self.content,
                 text="ℹ️  To update rates, run:  "
                      "UPDATE fare_rates SET base_fare=X, per_km_rate=Y "
                      "WHERE vehicle_type='Mini';",
                 font=config.FONT_SMALL,
                 bg=config.COLOR_BG, fg=config.COLOR_TEXT_LIGHT
                 ).pack(anchor="w", padx=20, pady=8)
