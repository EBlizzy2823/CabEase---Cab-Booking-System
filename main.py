# =============================================================
#  main.py — Entry point.  Run this to start the application.
#  > python main.py
# =============================================================

import tkinter as tk
from tkinter import messagebox
import config

from views.login_view              import LoginView
from views.register_customer_view  import RegisterCustomerView
from views.register_driver_view    import RegisterDriverView
from views.customer.customer_portal import CustomerPortal
from views.driver.driver_portal    import DriverPortal
from views.admin.admin_portal      import AdminPortal


class App(tk.Tk):
    """
    Root window — acts as the navigation controller.
    Swaps between views depending on login state and role.
    """

    def __init__(self):
        super().__init__()
        self.title(config.APP_TITLE)
        self.geometry(f"{config.APP_WIDTH}x{config.APP_HEIGHT}")
        self.minsize(900, 600)
        self.configure(bg=config.COLOR_BG)

        # Centre on screen
        self.update_idletasks()
        x = (self.winfo_screenwidth()  - config.APP_WIDTH)  // 2
        y = (self.winfo_screenheight() - config.APP_HEIGHT) // 2
        self.geometry(f"+{x}+{y}")

        self.current_user: dict | None = None
        self._view: tk.Frame | None    = None

        self.show_login()

    # ── View switcher ─────────────────────────────────────────

    def _swap(self, new_view: tk.Frame):
        if self._view:
            self._view.destroy()
        self._view = new_view
        new_view.pack(fill="both", expand=True)

    def show_login(self):
        self._swap(LoginView(self, self))

    def show_register_customer(self):
        self._swap(RegisterCustomerView(self, self))

    def show_register_driver(self):
        self._swap(RegisterDriverView(self, self))

    def show_dashboard(self):
        """Routes to the correct portal based on role."""
        if not self.current_user:
            self.show_login()
            return

        role = self.current_user["role"]
        if role == config.ROLE_CUSTOMER:
            self._swap(CustomerPortal(self, self, self.current_user))
        elif role == config.ROLE_DRIVER:
            self._swap(DriverPortal(self, self, self.current_user))
        elif role == config.ROLE_ADMIN:
            self._swap(AdminPortal(self, self, self.current_user))
        else:
            messagebox.showerror("Error", f"Unknown role: {role}")
            self.show_login()

    # ── Auth events ───────────────────────────────────────────

    def on_login_success(self, user: dict):
        self.current_user = user
        self.show_dashboard()

    def logout(self):
        if messagebox.askyesno("Logout", "Are you sure you want to log out?"):
            self.current_user = None
            self.show_login()


# ── Launch ────────────────────────────────────────────────────

if __name__ == "__main__":
    app = App()
    app.mainloop()
