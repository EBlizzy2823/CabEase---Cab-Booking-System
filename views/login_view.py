# =============================================================
#  views/login_view.py — Login screen (all roles)
# =============================================================

import tkinter as tk
from tkinter import messagebox
import sys, os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import config
from modules.auth import login_user


class LoginView(tk.Frame):

    def __init__(self, parent, app):
        super().__init__(parent, bg=config.COLOR_BG)
        self.app = app
        self._build()

    def _build(self):
        # ── Left panel ────────────────────────────────────────
        left = tk.Frame(self, bg=config.COLOR_PRIMARY, width=370)
        left.pack(side="left", fill="y")
        left.pack_propagate(False)

        tk.Label(left, text="🚖", font=("Helvetica", 64),
                 bg=config.COLOR_PRIMARY,
                 fg=config.COLOR_SECONDARY).pack(pady=(70, 6))

        tk.Label(left, text="Taxi Booking System",
                 font=("Helvetica", 20, "bold"),
                 bg=config.COLOR_PRIMARY,
                 fg=config.COLOR_WHITE).pack()

        tk.Label(left,
                 text="Tribhuvan University\nPatan Multiple Campus",
                 font=config.FONT_SMALL,
                 bg=config.COLOR_PRIMARY,
                 fg=config.COLOR_TEXT_LIGHT,
                 justify="center").pack(pady=(6, 0))

        # Role info boxes
        info = tk.Frame(left, bg=config.COLOR_PRIMARY)
        info.pack(pady=30)
        for icon, role in [("👤", "Customer"), ("🚗", "Driver"), ("🛡️", "Admin")]:
            row = tk.Frame(info, bg="#243342", padx=12, pady=6)
            row.pack(fill="x", pady=3, padx=20)
            tk.Label(row, text=f"{icon}  {role} Portal",
                     font=config.FONT_LABEL,
                     bg="#243342", fg="white").pack(anchor="w")

        # ── Right panel (form) ────────────────────────────────
        right = tk.Frame(self, bg=config.COLOR_BG)
        right.pack(side="right", fill="both", expand=True)

        form = tk.Frame(right, bg=config.COLOR_WHITE,
                        relief="flat", padx=40, pady=30)
        form.place(relx=0.5, rely=0.5, anchor="center", width=380)

        tk.Label(form, text="Sign In",
                 font=config.FONT_HEADING,
                 bg=config.COLOR_WHITE,
                 fg=config.COLOR_TEXT_DARK).pack(anchor="w")

        tk.Label(form, text="Enter your credentials to continue",
                 font=config.FONT_SMALL,
                 bg=config.COLOR_WHITE,
                 fg=config.COLOR_TEXT_LIGHT).pack(anchor="w",
                                                   pady=(2, 18))

        # Email
        self._lbl(form, "Email Address")
        self.email_var = tk.StringVar()
        self._ent(form, self.email_var)

        # Password
        self._lbl(form, "Password")
        self.pass_var = tk.StringVar()
        self._ent(form, self.pass_var, show="•")

        # Login button
        tk.Button(form, text="Login →",
                  font=config.FONT_BUTTON,
                  bg=config.COLOR_SECONDARY,
                  fg=config.COLOR_PRIMARY,
                  activebackground=config.COLOR_PRIMARY,
                  activeforeground="white",
                  relief="flat", cursor="hand2", height=2,
                  command=self._on_login
                  ).pack(fill="x", pady=(20, 10))

        # Divider
        tk.Frame(form, bg=config.COLOR_BORDER,
                 height=1).pack(fill="x", pady=8)

        # Register links
        reg_frame = tk.Frame(form, bg=config.COLOR_WHITE)
        reg_frame.pack()

        tk.Label(reg_frame, text="New here? Register as: ",
                 font=config.FONT_SMALL,
                 bg=config.COLOR_WHITE,
                 fg=config.COLOR_TEXT_LIGHT).grid(row=0, column=0,
                                                   columnspan=3)

        for col, (label, cmd) in enumerate([
            ("Customer", self.app.show_register_customer),
            ("Driver",   self.app.show_register_driver),
        ]):
            lnk = tk.Label(reg_frame, text=label,
                           font=(config.FONT_SMALL[0],
                                 config.FONT_SMALL[1], "underline"),
                           bg=config.COLOR_WHITE,
                           fg=config.COLOR_ACCENT,
                           cursor="hand2")
            lnk.grid(row=1, column=col, padx=10, pady=4)
            lnk.bind("<Button-1>", lambda e, c=cmd: c())

    # ── Helpers ───────────────────────────────────────────────

    def _lbl(self, p, text):
        tk.Label(p, text=text, font=config.FONT_SMALL,
                 bg=config.COLOR_WHITE,
                 fg=config.COLOR_TEXT_DARK,
                 anchor="w").pack(anchor="w", pady=(8, 2))

    def _ent(self, p, var, show=""):
        tk.Entry(p, textvariable=var,
                 font=config.FONT_NORMAL,
                 relief="solid", bd=1, show=show
                 ).pack(fill="x", ipady=6)

    def _on_login(self):
        email = self.email_var.get().strip()
        pw    = self.pass_var.get()

        if not email or not pw:
            messagebox.showwarning("Missing Fields",
                                   "Please enter your email and password.")
            return

        ok, msg, user = login_user(email, pw)
        if ok:
            self.pass_var.set("")
            self.app.on_login_success(user)
        else:
            messagebox.showerror("Login Failed", msg)
