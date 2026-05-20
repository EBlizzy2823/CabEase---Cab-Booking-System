# =============================================================
#  modules/driver.py — Driver profile & management logic
# =============================================================

import sys, os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from database.db_connection import execute_query
import config


# ── Get driver profile linked to a user_id ────────────────────

def get_driver_by_user_id(user_id: int) -> dict | None:
    rows = execute_query(
        """SELECT d.*, u.full_name, u.email, u.phone
             FROM drivers d
             JOIN users u ON d.user_id = u.id
            WHERE d.user_id = %s""",
        (user_id,), fetch=True
    )
    return rows[0] if rows else None


def get_driver_by_id(driver_id: int) -> dict | None:
    rows = execute_query(
        """SELECT d.*, u.full_name, u.email, u.phone
             FROM drivers d
             JOIN users u ON d.user_id = u.id
            WHERE d.id = %s""",
        (driver_id,), fetch=True
    )
    return rows[0] if rows else None


# ── All drivers (admin) ───────────────────────────────────────

def get_all_drivers() -> list[dict]:
    return execute_query(
        """SELECT d.*, u.full_name, u.email, u.phone
             FROM drivers d
             JOIN users u ON d.user_id = u.id
            ORDER BY d.created_at DESC""",
        fetch=True
    ) or []


def get_available_drivers(vehicle_type: str | None = None) -> list[dict]:
    """Returns drivers whose availability is 'Available'."""
    if vehicle_type:
        return execute_query(
            """SELECT d.*, u.full_name, u.phone
                 FROM drivers d
                 JOIN users u ON d.user_id = u.id
                WHERE d.availability = 'Available'
                  AND d.vehicle_type = %s
                ORDER BY d.rating DESC""",
            (vehicle_type,), fetch=True
        ) or []
    return execute_query(
        """SELECT d.*, u.full_name, u.phone
             FROM drivers d
             JOIN users u ON d.user_id = u.id
            WHERE d.availability = 'Available'
            ORDER BY d.rating DESC""",
        fetch=True
    ) or []


# ── Driver updates their own availability ─────────────────────

def update_availability(driver_id: int,
                         status: str) -> tuple[bool, str]:
    if status not in config.DRIVER_STATUSES:
        return False, f"Invalid status: {status}"
    execute_query(
        "UPDATE drivers SET availability=%s WHERE id=%s",
        (status, driver_id)
    )
    return True, f"Availability set to '{status}'."


# ── Admin updates driver details ──────────────────────────────

def admin_update_driver(driver_id: int, vehicle_type: str,
                         vehicle_number: str,
                         vehicle_model: str) -> tuple[bool, str]:
    execute_query(
        """UPDATE drivers
              SET vehicle_type=%s, vehicle_number=%s, vehicle_model=%s
            WHERE id=%s""",
        (vehicle_type, vehicle_number, vehicle_model, driver_id)
    )
    return True, "Driver profile updated."


def admin_delete_driver(user_id: int) -> tuple[bool, str]:
    execute_query("DELETE FROM users WHERE id=%s AND role='driver'",
                  (user_id,))
    return True, "Driver account deleted."


# ── Revenue per driver ────────────────────────────────────────

def get_driver_earnings(driver_id: int) -> dict:
    rows = execute_query(
        """SELECT COUNT(*)    AS total_trips,
                  SUM(fare)   AS total_earned
             FROM bookings
            WHERE driver_id=%s AND status='Completed'""",
        (driver_id,), fetch=True
    )
    if rows:
        return {
            "total_trips"  : rows[0]["total_trips"]  or 0,
            "total_earned" : float(rows[0]["total_earned"] or 0),
        }
    return {"total_trips": 0, "total_earned": 0.0}
