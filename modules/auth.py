# =============================================================
#  modules/auth.py — Authentication for all 3 roles
# =============================================================

import sys, os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from database.db_connection import execute_query
from modules.utils import hash_password, verify_password
import config


# ── Login (works for all roles) ───────────────────────────────

def login_user(email: str, password: str
               ) -> tuple[bool, str, dict | None]:
    rows = execute_query(
        "SELECT * FROM users WHERE email = %s", (email,), fetch=True
    )
    if not rows:
        return False, "No account found with that email.", None
    user = rows[0]
    if not verify_password(password, user["password"]):
        return False, "Incorrect password.", None
    return True, "Login successful!", user


# ── Customer registration ─────────────────────────────────────

def register_customer(full_name: str, email: str,
                      phone: str, password: str
                      ) -> tuple[bool, str]:
    if execute_query("SELECT id FROM users WHERE email=%s",
                     (email,), fetch=True):
        return False, "An account with this email already exists."

    row_id = execute_query(
        """INSERT INTO users (full_name, email, phone, password, role)
           VALUES (%s, %s, %s, %s, 'customer')""",
        (full_name, email, phone, hash_password(password))
    )
    return (True, "Registration successful!") if row_id \
        else (False, "Registration failed. Try again.")


# ── Driver registration ───────────────────────────────────────

def register_driver(full_name: str, email: str, phone: str,
                    password: str, license_number: str,
                    vehicle_type: str, vehicle_number: str,
                    vehicle_model: str) -> tuple[bool, str]:

    if execute_query("SELECT id FROM users WHERE email=%s",
                     (email,), fetch=True):
        return False, "An account with this email already exists."

    if execute_query("SELECT id FROM drivers WHERE license_number=%s",
                     (license_number,), fetch=True):
        return False, "This license number is already registered."

    # Insert into users
    user_id = execute_query(
        """INSERT INTO users (full_name, email, phone, password, role)
           VALUES (%s, %s, %s, %s, 'driver')""",
        (full_name, email, phone, hash_password(password))
    )
    if not user_id:
        return False, "Failed to create user account."

    # Insert into drivers
    drv_id = execute_query(
        """INSERT INTO drivers
               (user_id, license_number, vehicle_type,
                vehicle_number, vehicle_model)
           VALUES (%s, %s, %s, %s, %s)""",
        (user_id, license_number, vehicle_type,
         vehicle_number, vehicle_model)
    )
    return (True, "Driver registration successful!") if drv_id \
        else (False, "Failed to create driver profile.")


# ── Shared helpers ────────────────────────────────────────────

def get_user_by_id(user_id: int) -> dict | None:
    rows = execute_query("SELECT * FROM users WHERE id=%s",
                         (user_id,), fetch=True)
    return rows[0] if rows else None

def update_profile(user_id: int, full_name: str,
                   phone: str) -> tuple[bool, str]:
    execute_query(
        "UPDATE users SET full_name=%s, phone=%s WHERE id=%s",
        (full_name, phone, user_id)
    )
    return True, "Profile updated successfully."

def change_password(user_id: int, old_pw: str,
                    new_pw: str) -> tuple[bool, str]:
    rows = execute_query("SELECT password FROM users WHERE id=%s",
                         (user_id,), fetch=True)
    if not rows:
        return False, "User not found."
    if not verify_password(old_pw, rows[0]["password"]):
        return False, "Current password is incorrect."
    execute_query("UPDATE users SET password=%s WHERE id=%s",
                  (hash_password(new_pw), user_id))
    return True, "Password changed successfully."
