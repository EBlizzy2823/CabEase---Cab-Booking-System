# =============================================================
#  views/register_customer_view.py — Customer registration
# =============================================================

import tkinter as tk
from tkinter import messagebox
import sys, os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import config
from modules.auth  import register_customer
from modules.utils import (is_valid_email, is_valid_phone,
                            is_strong_password)


class RegisterCustomerView(tk.Frame):

    def __init__(self, parent, app):
        super().__init__(parent, bg=config.COLOR_BG)
        self.app = app
        self._build()

    def _build(self):
        # Left panel
        left = tk.Frame(self, bg=config.COLOR_INFO, width=340)
        left.pack(side="left", fill="y")
        left.pack_propagate(False)

        tk.Label(left, text="👤", font=("Helvetica", 56),
                 bg=config.COLOR_INFO, fg="white").pack(pady=(70, 6))
        tk.Label(left, text="Customer Portal",
                 font=("Helvetica", 18, "bold"),
                 bg=config.COLOR_INFO, fg="white").pack()
        tk.Label(left, text="Book taxis easily from\nyour desktop",
                 font=config.FONT_SMALL, justify="center",
                 bg=config.COLOR_INFO, fg="#AED6F1").pack(pady=8)

        # Perks list
        for perk in ["✅  Easy cab booking",
                     "✅  Track your rides",
                     "✅  View fare estimates",
                     "✅  Cancel anytime"]:
            tk.Label(left, text=perk, font=config.FONT_LABEL,
                     bg=config.COLOR_INFO, fg="white",
                     anchor="w").pack(padx=30, pady=2, anchor="w")

        # Right panel
        right = tk.Frame(self, bg=config.COLOR_BG)
        right.pack(side="right", fill="both", expand=True)

        card = tk.Frame(right, bg=config.COLOR_WHITE,
                        padx=36, pady=28)
        card.place(relx=0.5, rely=0.5, anchor="center", width=400)

        tk.Label(card, text="Create Customer Account",
                 font=config.FONT_SUBHEAD,
                 bg=config.COLOR_WHITE,
                 fg=config.COLOR_TEXT_DARK).pack(anchor="w")
        tk.Label(card, text="Fill in your details below",
                 font=config.FONT_SMALL,
                 bg=config.COLOR_WHITE,
                 fg=config.COLOR_TEXT_LIGHT).pack(anchor="w",
                                                   pady=(2, 16))

        fields = [
            ("Full Name",        "name_var",  ""),
            ("Email Address",    "email_var", ""),
            ("Phone Number",     "phone_var", ""),
            ("Password",         "pass_var",  "•"),
            ("Confirm Password", "cpass_var", "•"),
        ]
        for label, attr, show in fields:
            self._lbl(card, label)
            var = tk.StringVar()
            setattr(self, attr, var)
            tk.Entry(card, textvariable=var,
                     font=config.FONT_NORMAL,
                     relief="solid", bd=1, show=show
                     ).pack(fill="x", ipady=5, pady=(0, 4))

        tk.Button(card, text="Register as Customer",
                  font=config.FONT_BUTTON,
                  bg=config.COLOR_INFO, fg="white",
                  relief="flat", cursor="hand2", height=2,
                  command=self._register
                  ).pack(fill="x", pady=(14, 8))

        back = tk.Label(card, text="← Back to Login",
                        font=(config.FONT_SMALL[0],
                              config.FONT_SMALL[1], "underline"),
                        bg=config.COLOR_WHITE,
                        fg=config.COLOR_ACCENT, cursor="hand2")
        back.pack()
        back.bind("<Button-1>", lambda e: self.app.show_login())

    def _lbl(self, p, text):
        tk.Label(p, text=text, font=config.FONT_SMALL,
                 bg=config.COLOR_WHITE, fg=config.COLOR_TEXT_DARK,
                 anchor="w").pack(anchor="w", pady=(6, 1))

    def _register(self):
        name  = self.name_var.get().strip()
        email = self.email_var.get().strip()
        phone = self.phone_var.get().strip()
        pw    = self.pass_var.get()
        cpw   = self.cpass_var.get()

        if not all([name, email, phone, pw, cpw]):
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
        ok, reason = is_strong_password(pw)
        if not ok:
            messagebox.showerror("Weak Password", reason)
            return
        if pw != cpw:
            messagebox.showerror("Mismatch", "Passwords do not match.")
            return

        ok, msg = register_customer(name, email, phone, pw)
        if ok:
            messagebox.showinfo("Success", msg + "\nPlease log in.")
            self.app.show_login()
        else:
            messagebox.showerror("Failed", msg)
