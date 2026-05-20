# =============================================================
#  views/register_driver_view.py — Driver registration
# =============================================================

import tkinter as tk
from tkinter import ttk, messagebox
import sys, os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import config
from modules.auth  import register_driver
from modules.utils import (is_valid_email, is_valid_phone,
                            is_strong_password, is_valid_license)


class RegisterDriverView(tk.Frame):

    def __init__(self, parent, app):
        super().__init__(parent, bg=config.COLOR_BG)
        self.app = app
        self._build()

    def _build(self):
        # ── Left panel ────────────────────────────────────────
        left = tk.Frame(self, bg=config.COLOR_SUCCESS, width=340)
        left.pack(side="left", fill="y")
        left.pack_propagate(False)

        tk.Label(left, text="🚗", font=("Helvetica", 56),
                 bg=config.COLOR_SUCCESS, fg="white").pack(pady=(60, 6))
        tk.Label(left, text="Driver Portal",
                 font=("Helvetica", 18, "bold"),
                 bg=config.COLOR_SUCCESS, fg="white").pack()
        tk.Label(left, text="Join our driver network\nand earn more",
                 font=config.FONT_SMALL, justify="center",
                 bg=config.COLOR_SUCCESS, fg="#A9DFBF").pack(pady=8)

        for perk in ["✅  Manage your trips",
                     "✅  View assignments",
                     "✅  Track earnings",
                     "✅  Set availability"]:
            tk.Label(left, text=perk, font=config.FONT_LABEL,
                     bg=config.COLOR_SUCCESS, fg="white",
                     anchor="w").pack(padx=30, pady=2, anchor="w")

        tk.Label(left, text="License format: BA-01-PA-0012",
                 font=config.FONT_SMALL,
                 bg=config.COLOR_SUCCESS, fg="#A9DFBF"
                 ).pack(pady=(20, 0))

        # ── Right scroll canvas ───────────────────────────────
        right = tk.Frame(self, bg=config.COLOR_BG)
        right.pack(side="right", fill="both", expand=True)

        canvas = tk.Canvas(right, bg=config.COLOR_BG,
                           highlightthickness=0)
        scrollbar = ttk.Scrollbar(right, orient="vertical",
                                  command=canvas.yview)
        canvas.configure(yscrollcommand=scrollbar.set)
        scrollbar.pack(side="right", fill="y")
        canvas.pack(side="left", fill="both", expand=True)

        card = tk.Frame(canvas, bg=config.COLOR_WHITE,
                        padx=36, pady=28)
        canvas_win = canvas.create_window(
            (0, 0), window=card, anchor="nw"
        )

        def _on_configure(e):
            canvas.configure(scrollregion=canvas.bbox("all"))
            canvas.itemconfig(canvas_win, width=canvas.winfo_width())

        card.bind("<Configure>", _on_configure)
        canvas.bind("<Configure>", _on_configure)

        # ── Form fields ───────────────────────────────────────
        tk.Label(card, text="Create Driver Account",
                 font=config.FONT_SUBHEAD,
                 bg=config.COLOR_WHITE,
                 fg=config.COLOR_TEXT_DARK).pack(anchor="w")
        tk.Label(card, text="Personal info + vehicle details required",
                 font=config.FONT_SMALL,
                 bg=config.COLOR_WHITE,
                 fg=config.COLOR_TEXT_LIGHT).pack(anchor="w",
                                                   pady=(2, 14))

        # Personal info section
        self._section(card, "Personal Information")
        personal = [
            ("Full Name",     "name_var",  ""),
            ("Email Address", "email_var", ""),
            ("Phone Number",  "phone_var", ""),
            ("Password",      "pass_var",  "•"),
            ("Confirm Password","cpass_var","•"),
        ]
        for label, attr, show in personal:
            self._lbl(card, label)
            var = tk.StringVar()
            setattr(self, attr, var)
            tk.Entry(card, textvariable=var,
                     font=config.FONT_NORMAL,
                     relief="solid", bd=1, show=show
                     ).pack(fill="x", ipady=5, pady=(0, 4))

        # Vehicle info section
        self._section(card, "Vehicle Information")

        self._lbl(card, "License Number  (format: BA-01-PA-0012)")
        self.license_var = tk.StringVar()
        tk.Entry(card, textvariable=self.license_var,
                 font=config.FONT_NORMAL,
                 relief="solid", bd=1
                 ).pack(fill="x", ipady=5, pady=(0, 4))

        self._lbl(card, "Vehicle Type")
        self.vtype_var = tk.StringVar(value=config.VEHICLE_TYPES[0])
        vtype_cb = ttk.Combobox(card, textvariable=self.vtype_var,
                                 values=config.VEHICLE_TYPES,
                                 state="readonly",
                                 font=config.FONT_NORMAL)
        vtype_cb.pack(fill="x", pady=(0, 4))

        self._lbl(card, "Vehicle Number  (e.g. BA 1 PA 2024)")
        self.vnum_var = tk.StringVar()
        tk.Entry(card, textvariable=self.vnum_var,
                 font=config.FONT_NORMAL,
                 relief="solid", bd=1
                 ).pack(fill="x", ipady=5, pady=(0, 4))

        self._lbl(card, "Vehicle Model  (e.g. Toyota Vios)")
        self.vmodel_var = tk.StringVar()
        tk.Entry(card, textvariable=self.vmodel_var,
                 font=config.FONT_NORMAL,
                 relief="solid", bd=1
                 ).pack(fill="x", ipady=5, pady=(0, 4))

        tk.Button(card, text="Register as Driver",
                  font=config.FONT_BUTTON,
                  bg=config.COLOR_SUCCESS, fg="white",
                  relief="flat", cursor="hand2", height=2,
                  command=self._register
                  ).pack(fill="x", pady=(16, 8))

        back = tk.Label(card, text="← Back to Login",
                        font=(config.FONT_SMALL[0],
                              config.FONT_SMALL[1], "underline"),
                        bg=config.COLOR_WHITE,
                        fg=config.COLOR_ACCENT, cursor="hand2")
        back.pack()
        back.bind("<Button-1>", lambda e: self.app.show_login())

    def _section(self, p, text):
        tk.Label(p, text=text, font=("Helvetica", 10, "bold"),
                 bg=config.COLOR_WHITE,
                 fg=config.COLOR_PRIMARY).pack(anchor="w",
                                               pady=(14, 4))

    def _lbl(self, p, text):
        tk.Label(p, text=text, font=config.FONT_SMALL,
                 bg=config.COLOR_WHITE, fg=config.COLOR_TEXT_DARK,
                 anchor="w").pack(anchor="w", pady=(4, 1))

    def _register(self):
        name    = self.name_var.get().strip()
        email   = self.email_var.get().strip()
        phone   = self.phone_var.get().strip()
        pw      = self.pass_var.get()
        cpw     = self.cpass_var.get()
        lic     = self.license_var.get().strip().upper()
        vtype   = self.vtype_var.get()
        vnum    = self.vnum_var.get().strip().upper()
        vmodel  = self.vmodel_var.get().strip()

        if not all([name, email, phone, pw, cpw, lic, vnum, vmodel]):
            messagebox.showwarning("Missing", "Please fill in all fields.")
            return
        if not is_valid_email(email):
            messagebox.showerror("Invalid Email",
                                 "Please enter a valid email address.")
            return
        if not is_valid_phone(phone):
            messagebox.showerror("Invalid Phone",
                                 "Enter a valid 10-digit Nepali number.")
            return
        if not is_valid_license(lic):
            messagebox.showerror("Invalid License",
                                 "Format must be: BA-01-PA-0012")
            return
        ok, reason = is_strong_password(pw)
        if not ok:
            messagebox.showerror("Weak Password", reason)
            return
        if pw != cpw:
            messagebox.showerror("Mismatch", "Passwords do not match.")
            return

        ok, msg = register_driver(name, email, phone, pw,
                                   lic, vtype, vnum, vmodel)
        if ok:
            messagebox.showinfo("Success", msg + "\nPlease log in.")
            self.app.show_login()
        else:
            messagebox.showerror("Failed", msg)
