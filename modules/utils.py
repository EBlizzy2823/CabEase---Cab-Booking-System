# =============================================================
#  modules/utils.py — Shared utility functions
# =============================================================

import hashlib, re
from datetime import datetime
import sys, os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import config


# ── Security ──────────────────────────────────────────────────

def hash_password(password: str) -> str:
    return hashlib.sha256(password.encode()).hexdigest()

def verify_password(plain: str, hashed: str) -> bool:
    return hash_password(plain) == hashed


# ── Validation ────────────────────────────────────────────────

def is_valid_email(email: str) -> bool:
    return bool(re.match(r"^[\w\.-]+@[\w\.-]+\.\w{2,}$", email))

def is_valid_phone(phone: str) -> bool:
    phone = phone.replace(" ", "").replace("-", "")
    return bool(re.match(r"^(\+977)?[9][6-9]\d{8}$", phone))

def is_valid_license(lic: str) -> bool:
    """Basic Nepal license format: e.g. BA-01-PA-0012"""
    return bool(re.match(r"^[A-Z]{2}-\d{2}-[A-Z]{2}-\d{4}$", lic))

def is_strong_password(pw: str) -> tuple[bool, str]:
    if len(pw) < 8:
        return False, "Password must be at least 8 characters."
    if not re.search(r"[A-Z]", pw):
        return False, "Must contain at least one uppercase letter."
    if not re.search(r"[0-9]", pw):
        return False, "Must contain at least one digit."
    if not re.search(r"[!@#$%^&*]", pw):
        return False, "Must contain at least one special character (!@#$%^&*)."
    return True, ""


# ── Fare calculation ──────────────────────────────────────────

def calculate_fare(vehicle_type: str, distance_km: float) -> float:
    base = config.BASE_FARE.get(vehicle_type, 50)
    rate = config.PER_KM.get(vehicle_type, 12)
    return round(base + rate * distance_km, 2)

# REPLACE with this:
def estimate_distance(pickup: str, dropoff: str) -> float:
    """
    Calculates real road distance using OpenRouteService API
    with Haversine as a fallback.
    """
    from modules.map_utils import calculate_distance_between_places
    return calculate_distance_between_places(pickup, dropoff)


# ── Formatting ────────────────────────────────────────────────

def now_str() -> str:
    return datetime.now().strftime("%Y-%m-%d %H:%M:%S")

def format_datetime(dt) -> str:
    if isinstance(dt, datetime):
        return dt.strftime("%d %b %Y, %I:%M %p")
    return str(dt)

def format_currency(amount) -> str:
    try:
        return f"NPR {float(amount):,.2f}"
    except (TypeError, ValueError):
        return "NPR 0.00"
