# =============================================================
#  modules/booking.py — Booking business logic
# =============================================================

import sys, os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from database.db_connection import execute_query
from modules.utils import calculate_fare, estimate_distance
import config


# ── Create booking (customer) ─────────────────────────────────

def create_booking(customer_id: int, pickup: str, dropoff: str,
                   vehicle_type: str, booking_date: str,
                   booking_time: str, notes: str = ""
                   ) -> tuple[bool, str, int | None]:

    distance = estimate_distance(pickup, dropoff)
    fare     = calculate_fare(vehicle_type, distance)

    row_id = execute_query(
        """INSERT INTO bookings
               (customer_id, pickup_location, dropoff_location,
                vehicle_type, booking_date, booking_time,
                fare, distance_km, notes, status)
           VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,'Pending')""",
        (customer_id, pickup, dropoff, vehicle_type,
         booking_date, booking_time, fare, distance, notes)
    )

    if row_id:
        return (True,
                f"Booking confirmed! Estimated fare: NPR {fare:.2f}",
                row_id)
    return False, "Booking failed. Please try again.", None


# ── Customer: view own bookings ───────────────────────────────

def get_customer_bookings(customer_id: int) -> list[dict]:
    return execute_query(
        """SELECT b.*,
                  u.full_name  AS driver_name,
                  d.vehicle_number, d.vehicle_model
             FROM bookings b
             LEFT JOIN drivers d  ON b.driver_id  = d.id
             LEFT JOIN users   u  ON d.user_id     = u.id
            WHERE b.customer_id = %s
            ORDER BY b.created_at DESC""",
        (customer_id,), fetch=True
    ) or []


def cancel_booking(booking_id: int,
                   customer_id: int) -> tuple[bool, str]:
    rows = execute_query(
        "SELECT status FROM bookings WHERE id=%s AND customer_id=%s",
        (booking_id, customer_id), fetch=True
    )
    if not rows:
        return False, "Booking not found."
    if rows[0]["status"] != config.STATUS_PENDING:
        return False, "Only Pending bookings can be cancelled."
    execute_query(
        "UPDATE bookings SET status='Cancelled' WHERE id=%s",
        (booking_id,)
    )
    return True, "Booking cancelled successfully."


# ── Driver: view assigned bookings ────────────────────────────

def get_driver_bookings(driver_id: int) -> list[dict]:
    return execute_query(
        """SELECT b.*,
                  cu.full_name AS customer_name,
                  cu.phone     AS customer_phone
             FROM bookings b
             JOIN users cu ON b.customer_id = cu.id
            WHERE b.driver_id = %s
            ORDER BY b.booking_date DESC, b.booking_time DESC""",
        (driver_id,), fetch=True
    ) or []


def driver_update_trip_status(booking_id: int,
                               driver_id: int,
                               new_status: str) -> tuple[bool, str]:
    """Driver can move a booking from Confirmed → Completed."""
    allowed = {config.STATUS_COMPLETED}
    if new_status not in allowed:
        return False, "Drivers can only mark trips as Completed."

    rows = execute_query(
        "SELECT status, driver_id FROM bookings WHERE id=%s",
        (booking_id,), fetch=True
    )
    if not rows:
        return False, "Booking not found."
    if rows[0]["driver_id"] != driver_id:
        return False, "This booking is not assigned to you."
    if rows[0]["status"] != config.STATUS_CONFIRMED:
        return False, "Only Confirmed bookings can be marked Completed."

    execute_query(
        "UPDATE bookings SET status='Completed' WHERE id=%s",
        (booking_id,)
    )
    # Increment driver's total trips
    execute_query(
        "UPDATE drivers SET total_trips = total_trips+1 WHERE id=%s",
        (driver_id,)
    )
    return True, "Trip marked as Completed."


# ── Admin: all bookings ───────────────────────────────────────

def get_all_bookings() -> list[dict]:
    return execute_query(
        """SELECT b.*,
                  cu.full_name  AS customer_name,
                  cu.phone      AS customer_phone,
                  du.full_name  AS driver_name,
                  d.vehicle_number
             FROM bookings b
             JOIN  users cu ON b.customer_id = cu.id
             LEFT JOIN drivers d  ON b.driver_id  = d.id
             LEFT JOIN users   du ON d.user_id     = du.id
            ORDER BY b.created_at DESC""",
        fetch=True
    ) or []


def assign_driver(booking_id: int,
                  driver_id: int) -> tuple[bool, str]:
    # Check driver is available
    drv = execute_query(
        "SELECT availability FROM drivers WHERE id=%s",
        (driver_id,), fetch=True
    )
    if not drv:
        return False, "Driver not found."
    if drv[0]["availability"] == config.DRIVER_ON_TRIP:
        return False, "Driver is currently on another trip."

    execute_query(
        """UPDATE bookings
              SET driver_id=%s, status='Confirmed'
            WHERE id=%s""",
        (driver_id, booking_id)
    )
    execute_query(
        "UPDATE drivers SET availability='On Trip' WHERE id=%s",
        (driver_id,)
    )
    return True, "Driver assigned and booking confirmed."


def admin_update_booking_status(booking_id: int,
                                 status: str) -> tuple[bool, str]:
    if status not in config.BOOKING_STATUSES:
        return False, "Invalid status."

    # If cancelling, free the driver
    if status == config.STATUS_CANCELLED:
        rows = execute_query(
            "SELECT driver_id FROM bookings WHERE id=%s",
            (booking_id,), fetch=True
        )
        if rows and rows[0]["driver_id"]:
            execute_query(
                "UPDATE drivers SET availability='Available' WHERE id=%s",
                (rows[0]["driver_id"],)
            )

    execute_query(
        "UPDATE bookings SET status=%s WHERE id=%s",
        (status, booking_id)
    )
    return True, f"Booking #{booking_id} updated to '{status}'."


# ── Stats for admin dashboard ─────────────────────────────────

def get_dashboard_stats() -> dict:
    def _count(q, p=()):
        r = execute_query(q, p, fetch=True)
        return r[0]["cnt"] if r else 0

    def _sum(q):
        r = execute_query(q, fetch=True)
        return float(r[0]["total"] or 0) if r else 0.0

    return {
        "total_bookings" : _count("SELECT COUNT(*) AS cnt FROM bookings"),
        "pending"        : _count("SELECT COUNT(*) AS cnt FROM bookings WHERE status='Pending'"),
        "confirmed"      : _count("SELECT COUNT(*) AS cnt FROM bookings WHERE status='Confirmed'"),
        "completed"      : _count("SELECT COUNT(*) AS cnt FROM bookings WHERE status='Completed'"),
        "cancelled"      : _count("SELECT COUNT(*) AS cnt FROM bookings WHERE status='Cancelled'"),
        "total_customers": _count("SELECT COUNT(*) AS cnt FROM users WHERE role='customer'"),
        "total_drivers"  : _count("SELECT COUNT(*) AS cnt FROM users WHERE role='driver'"),
        "revenue"        : _sum("SELECT SUM(fare) AS total FROM bookings WHERE status='Completed'"),
    }
