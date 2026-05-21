import tkinter as tk
from tkinter import ttk, messagebox
from tkcalendar import DateEntry
import threading
import sys, os
sys.path.append(os.path.dirname(os.path.dirname(
    os.path.dirname(os.path.abspath(__file__)))))

import config
from modules.widgets import (make_topbar, make_sidebar,
                              stat_card, make_tree,
                              section_title, section_subtitle)
from modules.booking import (get_customer_bookings, create_booking,
                              cancel_booking)
from modules.utils   import calculate_fare


class CustomerPortal(tk.Frame):

    def __init__(self, parent, app, user: dict):
        super().__init__(parent, bg=config.COLOR_BG)
        self.app  = app
        self.user = user

        make_topbar(self,
                    title="Taxi Booking System",
                    user_name=self.user["full_name"],
                    logout_cmd=self.app.logout,
                    role_color=config.COLOR_INFO)

        body = tk.Frame(self, bg=config.COLOR_BG)
        body.pack(fill="both", expand=True)

        make_sidebar(body, [
            ("🏠  Dashboard",   self._tab_dashboard),
            ("🚕  Book a Cab",  self._tab_book),
            ("📋  My Bookings", self._tab_my_bookings),
            ("👤  My Profile",  self._tab_profile),
        ])

        self.content = tk.Frame(body, bg=config.COLOR_BG)
        self.content.pack(side="right", fill="both", expand=True)

        self._tab_dashboard()

    # ── Clear ─────────────────────────────────────────────────

    def _clear(self):
        for w in self.content.winfo_children():
            w.destroy()

    # ── Scrollable content wrapper ────────────────────────────

    def _make_scrollable(self) -> tk.Frame:
        """
        Replaces self.content with a canvas + scrollbar so tall
        pages like the booking form are fully reachable.
        Returns an inner frame to place widgets into.
        """
        canvas = tk.Canvas(self.content, bg=config.COLOR_BG,
                           highlightthickness=0)
        vsb    = ttk.Scrollbar(self.content, orient="vertical",
                               command=canvas.yview)
        canvas.configure(yscrollcommand=vsb.set)

        vsb.pack(side="right", fill="y")
        canvas.pack(side="left", fill="both", expand=True)

        inner = tk.Frame(canvas, bg=config.COLOR_BG)
        win   = canvas.create_window((0, 0), window=inner, anchor="nw")

        def _on_frame_configure(e):
            canvas.configure(scrollregion=canvas.bbox("all"))

        def _on_canvas_configure(e):
            canvas.itemconfig(win, width=e.width)

        inner.bind("<Configure>", _on_frame_configure)
        canvas.bind("<Configure>", _on_canvas_configure)

        # Mouse wheel scrolling
        def _on_mousewheel(e):
            canvas.yview_scroll(int(-1 * (e.delta / 120)), "units")

        canvas.bind_all("<MouseWheel>", _on_mousewheel)

        return inner

    # ── Tab: Dashboard ────────────────────────────────────────

    def _tab_dashboard(self):
        self._clear()
        section_title(self.content,
                      f"Welcome, {self.user['full_name'].split()[0]}! 👋")
        section_subtitle(self.content,
                         "Here's a summary of your travel activity")

        bookings  = get_customer_bookings(self.user["id"])
        total     = len(bookings)
        pending   = sum(1 for b in bookings if b["status"] == "Pending")
        completed = sum(1 for b in bookings if b["status"] == "Completed")

        cards = tk.Frame(self.content, bg=config.COLOR_BG)
        cards.pack(padx=20, pady=4, anchor="w")
        stat_card(cards, "Total Bookings", total,        config.COLOR_INFO,    0)
        stat_card(cards, "Pending",        pending,      config.COLOR_WARNING, 1)
        stat_card(cards, "Completed",      completed,    config.COLOR_SUCCESS, 2)

        section_title(self.content, "Recent Bookings")
        cols    = ("ID", "Pickup", "Dropoff", "Vehicle", "Date",
                   "Fare", "Driver", "Status")
        widths  = (40, 140, 140, 70, 100, 90, 110, 90)
        tree, _ = make_tree(self.content, cols, widths, height=9)
        self._fill_tree(tree, bookings[:8])

        tk.Button(self.content, text="+ Book a New Cab",
                  font=config.FONT_BUTTON,
                  bg=config.COLOR_SECONDARY, fg=config.COLOR_PRIMARY,
                  relief="flat", cursor="hand2", padx=14, pady=6,
                  command=self._tab_book
                  ).pack(anchor="w", padx=20, pady=10)

    # ── Tab: Book a cab ───────────────────────────────────────

    def _tab_book(self):
        self._clear()

        # Use a scrollable inner frame so nothing gets cut off
        page = self._make_scrollable()

        section_title(page, "Book a Cab 🚕")
        section_subtitle(page, "Search for your locations or type them in")

        # ── Location card ──────────────────────────────────────
        loc = tk.Frame(page, bg=config.COLOR_WHITE, padx=28, pady=18)
        loc.pack(padx=20, pady=(4, 8), fill="x")

        tk.Label(loc, text="Select Locations",
                 font=("Helvetica", 11, "bold"),
                 bg=config.COLOR_WHITE,
                 fg=config.COLOR_TEXT_DARK
                 ).pack(anchor="w", pady=(0, 10))

        self.pickup_var  = tk.StringVar()
        self.dropoff_var = tk.StringVar()
        self._pickup_coords  = None
        self._dropoff_coords = None

        for label, var, field in [
            ("📍 Pickup:",   self.pickup_var,  "pickup"),
            ("🏁 Drop-off:", self.dropoff_var, "dropoff"),
        ]:
            row = tk.Frame(loc, bg=config.COLOR_WHITE)
            row.pack(fill="x", pady=(0, 8))
            tk.Label(row, text=label, font=config.FONT_LABEL,
                     width=10, bg=config.COLOR_WHITE,
                     fg=config.COLOR_TEXT_DARK,
                     anchor="w").pack(side="left")
            tk.Entry(row, textvariable=var,
                     font=config.FONT_NORMAL,
                     width=36, relief="solid", bd=1
                     ).pack(side="left", ipady=5, padx=(0, 8))
            tk.Button(row, text="📌 Pin on Map",
                      font=config.FONT_SMALL,
                      bg=config.COLOR_INFO, fg="white",
                      relief="flat", cursor="hand2", padx=8, pady=4,
                      command=lambda f=field: self._open_map(f)
                      ).pack(side="left")

        # ── Trip details card ──────────────────────────────────
        det = tk.Frame(page, bg=config.COLOR_WHITE, padx=28, pady=18)
        det.pack(padx=20, pady=(0, 8), fill="x")

        tk.Label(det, text="Trip Details",
                 font=("Helvetica", 11, "bold"),
                 bg=config.COLOR_WHITE,
                 fg=config.COLOR_TEXT_DARK
                 ).pack(anchor="w", pady=(0, 10))

        # Vehicle type
        tk.Label(det, text="🚗 Vehicle Type:",
                 font=config.FONT_LABEL,
                 bg=config.COLOR_WHITE,
                 fg=config.COLOR_TEXT_DARK).pack(anchor="w")

        self.vtype_var = tk.StringVar(value=config.VEHICLE_TYPES[0])
        vrow = tk.Frame(det, bg=config.COLOR_WHITE)
        vrow.pack(anchor="w", pady=(4, 10))
        for vt in config.VEHICLE_TYPES:
            tk.Radiobutton(vrow, text=vt,
                           variable=self.vtype_var, value=vt,
                           font=config.FONT_NORMAL,
                           bg=config.COLOR_WHITE,
                           activebackground=config.COLOR_WHITE,
                           command=self._refresh_fare
                           ).pack(side="left", padx=10)

        # Date & Time on one row
        dt_row = tk.Frame(det, bg=config.COLOR_WHITE)
        dt_row.pack(anchor="w", pady=(0, 10))

        df = tk.Frame(dt_row, bg=config.COLOR_WHITE)
        df.pack(side="left", padx=(0, 30))
        tk.Label(df, text="📅 Date:", font=config.FONT_LABEL,
                 bg=config.COLOR_WHITE,
                 fg=config.COLOR_TEXT_DARK).pack(anchor="w")
        self.date_entry = DateEntry(df, font=config.FONT_NORMAL,
                                    width=14, date_pattern="yyyy-mm-dd",
                                    relief="solid")
        self.date_entry.pack(anchor="w")

        tf = tk.Frame(dt_row, bg=config.COLOR_WHITE)
        tf.pack(side="left")
        tk.Label(tf, text="⏰ Time (HH:MM):", font=config.FONT_LABEL,
                 bg=config.COLOR_WHITE,
                 fg=config.COLOR_TEXT_DARK).pack(anchor="w")
        self.time_var = tk.StringVar(value="10:00")
        tk.Entry(tf, textvariable=self.time_var,
                 font=config.FONT_NORMAL, width=10,
                 relief="solid", bd=1).pack(anchor="w", ipady=4)

        # Notes
        tk.Label(det, text="📝 Notes (optional):",
                 font=config.FONT_LABEL,
                 bg=config.COLOR_WHITE,
                 fg=config.COLOR_TEXT_DARK).pack(anchor="w")
        self.notes_var = tk.StringVar()
        tk.Entry(det, textvariable=self.notes_var,
                 font=config.FONT_NORMAL, width=50,
                 relief="solid", bd=1
                 ).pack(anchor="w", ipady=5, pady=(4, 0))

        # ── Fare + Confirm card (combined) ────────────────────
        fare_card = tk.Frame(page, bg=config.COLOR_WHITE,
                             padx=28, pady=18)
        fare_card.pack(padx=20, pady=(0, 8), fill="x")

        tk.Label(fare_card, text="Fare & Booking",
                 font=("Helvetica", 11, "bold"),
                 bg=config.COLOR_WHITE,
                 fg=config.COLOR_TEXT_DARK
                 ).pack(anchor="w", pady=(0, 10))

        # Fare display row
        fare_row = tk.Frame(fare_card, bg=config.COLOR_WHITE)
        fare_row.pack(fill="x", pady=(0, 6))

        self.fare_lbl = tk.Label(fare_row,
                                  text="💰  Estimated Fare: —",
                                  font=config.FONT_SUBHEAD,
                                  bg=config.COLOR_WHITE,
                                  fg=config.COLOR_SUCCESS)
        self.fare_lbl.pack(side="left")

        self.dist_lbl = tk.Label(fare_row, text="",
                                  font=config.FONT_SMALL,
                                  bg=config.COLOR_WHITE,
                                  fg=config.COLOR_TEXT_LIGHT)
        self.dist_lbl.pack(side="left", padx=16)

        # Button row — Calculate + Confirm side by side
        btn_row = tk.Frame(fare_card, bg=config.COLOR_WHITE)
        btn_row.pack(anchor="w", pady=(4, 0))

        self.calc_btn = tk.Button(btn_row,
                                   text="🔄  Calculate Fare",
                                   font=config.FONT_BUTTON,
                                   bg=config.COLOR_WARNING, fg="white",
                                   relief="flat", cursor="hand2",
                                   padx=16, pady=8,
                                   command=self._refresh_fare)
        self.calc_btn.pack(side="left", padx=(0, 12))

        tk.Button(btn_row,
                  text="✓  Confirm Booking",
                  font=config.FONT_BUTTON,
                  bg=config.COLOR_SECONDARY, fg=config.COLOR_PRIMARY,
                  relief="flat", cursor="hand2",
                  padx=16, pady=8,
                  command=self._confirm_booking
                  ).pack(side="left")

        tk.Label(fare_card,
                 text="ℹ️  Calculate fare first, then confirm your booking.",
                 font=config.FONT_SMALL,
                 bg=config.COLOR_WHITE, fg=config.COLOR_TEXT_LIGHT
                 ).pack(anchor="w", pady=(8, 0))

        # Reset fare when locations are changed manually
        self.pickup_var.trace_add("write",  lambda *_: self._clear_fare())
        self.dropoff_var.trace_add("write", lambda *_: self._clear_fare())

    # ── Map opener ────────────────────────────────────────────

    def _open_map(self, field: str):
        label = ("Pickup Location" if field == "pickup"
                 else "Drop-off Location")

        def on_selected(place_name: str, lat, lng):
            if field == "pickup":
                self.pickup_var.set(place_name)
                self._pickup_coords = (lat, lng) if lat else None
            else:
                self.dropoff_var.set(place_name)
                self._dropoff_coords = (lat, lng) if lat else None

        from views.customer.map_picker import MapPickerWindow
        MapPickerWindow(self, label, on_selected)

    # ── Fare helpers ──────────────────────────────────────────

    def _clear_fare(self):
        try:
            self.fare_lbl.config(text="💰  Estimated Fare: —",
                                 fg=config.COLOR_SUCCESS)
            self.dist_lbl.config(text="")
        except Exception:
            pass

    def _refresh_fare(self):
        pickup  = self.pickup_var.get().strip()
        dropoff = self.dropoff_var.get().strip()

        if not pickup or not dropoff:
            self._clear_fare()
            return

        self.fare_lbl.config(text="⏳  Calculating…",
                              fg=config.COLOR_TEXT_LIGHT)
        self.dist_lbl.config(text="")
        self.calc_btn.config(state="disabled")
        self.update()

        from modules.map_utils import (calculate_distance_between_places,
                                        get_road_distance_km)

        def compute():
            try:
                if self._pickup_coords and self._dropoff_coords:
                    dist = get_road_distance_km(
                        self._pickup_coords[0], self._pickup_coords[1],
                        self._dropoff_coords[0], self._dropoff_coords[1]
                    )
                else:
                    dist = calculate_distance_between_places(
                        pickup, dropoff
                    )
                fare = calculate_fare(self.vtype_var.get(), dist or 5.0)
                self.after(0, lambda: self._show_fare(fare, dist or 5.0))
            except Exception as e:
                print(f"[FARE ERROR] {e}")
                self.after(0, self._fare_error)

        threading.Thread(target=compute, daemon=True).start()

    def _show_fare(self, fare: float, dist: float):
        try:
            self.fare_lbl.config(
                text=f"💰  Estimated Fare:  NPR {fare:,.2f}",
                fg=config.COLOR_SUCCESS
            )
            self.dist_lbl.config(
                text=f"({dist:.1f} km road distance)"
            )
            self.calc_btn.config(state="normal")
        except Exception:
            pass

    def _fare_error(self):
        try:
            self.fare_lbl.config(
                text="⚠️  Could not calculate. Check internet connection.",
                fg=config.COLOR_DANGER
            )
            self.calc_btn.config(state="normal")
        except Exception:
            pass

    # ── Booking submission ────────────────────────────────────

    def _confirm_booking(self):
        pickup  = self.pickup_var.get().strip()
        dropoff = self.dropoff_var.get().strip()
        vtype   = self.vtype_var.get()
        date    = self.date_entry.get_date()
        time    = self.time_var.get().strip()
        notes   = self.notes_var.get().strip()

        if not pickup or not dropoff:
            messagebox.showwarning("Missing",
                                   "Please enter pickup and drop-off locations.")
            return
        if not time or ":" not in time:
            messagebox.showwarning("Invalid Time",
                                   "Please enter time as HH:MM (e.g. 14:30).")
            return

        ok, msg, _ = create_booking(
            self.user["id"], pickup, dropoff, vtype,
            str(date), time + ":00", notes
        )
        if ok:
            messagebox.showinfo("Booking Confirmed! 🎉", msg)
            self._tab_my_bookings()
        else:
            messagebox.showerror("Failed", msg)

    # ── Tab: My Bookings ──────────────────────────────────────

    def _tab_my_bookings(self):
        self._clear()
        section_title(self.content, "My Bookings 📋")
        section_subtitle(self.content,
                         "All your cab rides — colour-coded by status")

        cols   = ("ID", "Pickup", "Dropoff", "Vehicle", "Date",
                  "Time", "Fare", "Driver", "Vehicle No.", "Status")
        widths = (40, 130, 130, 65, 100, 70, 85, 110, 100, 85)
        self.my_tree, _ = make_tree(self.content, cols, widths, height=15)
        bookings = get_customer_bookings(self.user["id"])
        self._fill_tree(self.my_tree, bookings)

        ctrl = tk.Frame(self.content, bg=config.COLOR_BG)
        ctrl.pack(anchor="w", padx=20, pady=8)

        tk.Button(ctrl, text="🔄  Refresh",
                  font=config.FONT_BUTTON,
                  bg=config.COLOR_INFO, fg="white",
                  relief="flat", cursor="hand2", padx=12, pady=4,
                  command=self._tab_my_bookings
                  ).pack(side="left", padx=(0, 8))

        tk.Button(ctrl, text="❌  Cancel Selected",
                  font=config.FONT_BUTTON,
                  bg=config.COLOR_DANGER, fg="white",
                  relief="flat", cursor="hand2", padx=12, pady=4,
                  command=self._cancel_selected
                  ).pack(side="left")

    def _cancel_selected(self):
        sel = self.my_tree.selection()
        if not sel:
            messagebox.showinfo("No Selection",
                                "Please select a booking to cancel.")
            return
        bid = int(self.my_tree.item(sel[0], "values")[0])
        if not messagebox.askyesno("Confirm", f"Cancel Booking #{bid}?"):
            return
        ok, msg = cancel_booking(bid, self.user["id"])
        if ok:
            messagebox.showinfo("Done", msg)
            self._tab_my_bookings()
        else:
            messagebox.showerror("Error", msg)

    # ── Tab: Profile ──────────────────────────────────────────

    def _tab_profile(self):
        self._clear()
        section_title(self.content, "My Profile 👤")

        card = tk.Frame(self.content, bg=config.COLOR_WHITE,
                        padx=36, pady=30)
        card.pack(padx=20, pady=10, anchor="nw")

        for i, (label, value) in enumerate([
            ("Full Name",    self.user["full_name"]),
            ("Email",        self.user["email"]),
            ("Phone",        self.user["phone"]),
            ("Role",         "Customer"),
            ("Member Since", str(self.user.get("created_at", ""))),
        ]):
            tk.Label(card, text=f"{label}:",
                     font=("Helvetica", 10, "bold"),
                     bg=config.COLOR_WHITE, fg=config.COLOR_TEXT_DARK,
                     width=14, anchor="w"
                     ).grid(row=i, column=0, sticky="w", pady=6)
            tk.Label(card, text=value,
                     font=config.FONT_NORMAL,
                     bg=config.COLOR_WHITE, fg=config.COLOR_TEXT_LIGHT
                     ).grid(row=i, column=1, sticky="w", padx=10)

    # ── Tree filler ───────────────────────────────────────────

    def _fill_tree(self, tree, bookings):
        for row in tree.get_children():
            tree.delete(row)
        if not bookings:
            tree.insert("", "end",
                        values=("—", "No bookings yet",
                                "", "", "", "", "", "", "", ""))
            return
        for b in bookings:
            driver = b.get("driver_name") or "Not Assigned"
            vno    = b.get("vehicle_number") or "—"
            tree.insert("", "end",
                        values=(b["id"],
                                b["pickup_location"],
                                b["dropoff_location"],
                                b["vehicle_type"],
                                str(b["booking_date"]),
                                str(b.get("booking_time", "")),
                                f"NPR {b['fare']:.2f}",
                                driver, vno, b["status"]),
                        tags=(b["status"],))