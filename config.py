# =============================================================
#  config.py — Application-wide settings
#  ✏️  Change DB_PASSWORD to match your MySQL root password
# =============================================================

# ── Database ──────────────────────────────────────────────────
DB_HOST     = "localhost"
DB_USER     = "root"
DB_PASSWORD = "Change this"          # ← Change this
DB_NAME     = "taxi_booking_db"

# ── Application ───────────────────────────────────────────────
APP_TITLE   = "Desktop Based Taxi Booking System"
APP_WIDTH   = 1000
APP_HEIGHT  = 650

# ── User roles ────────────────────────────────────────────────
ROLE_ADMIN    = "admin"
ROLE_CUSTOMER = "customer"
ROLE_DRIVER   = "driver"

# ── Cab / vehicle types and fare rates ────────────────────────
VEHICLE_TYPES = ["Mini", "Sedan", "SUV", "Luxury"]

BASE_FARE = {"Mini": 50,  "Sedan": 80,  "SUV": 120, "Luxury": 200}
PER_KM    = {"Mini": 12,  "Sedan": 15,  "SUV": 20,  "Luxury": 30}

# ── Driver availability statuses ──────────────────────────────
DRIVER_AVAILABLE   = "Available"
DRIVER_ON_TRIP     = "On Trip"
DRIVER_OFFLINE     = "Offline"
DRIVER_STATUSES    = [DRIVER_AVAILABLE, DRIVER_ON_TRIP, DRIVER_OFFLINE]

# ── Booking statuses ──────────────────────────────────────────
STATUS_PENDING   = "Pending"
STATUS_CONFIRMED = "Confirmed"
STATUS_COMPLETED = "Completed"
STATUS_CANCELLED = "Cancelled"
BOOKING_STATUSES = [STATUS_PENDING, STATUS_CONFIRMED,
                    STATUS_COMPLETED, STATUS_CANCELLED]

# ── Theme colours ─────────────────────────────────────────────
COLOR_PRIMARY    = "#1A252F"   # Dark navy
COLOR_SECONDARY  = "#F4D03F"   # Taxi yellow
COLOR_ACCENT     = "#E67E22"   # Orange
COLOR_BG         = "#F2F3F4"   # Light grey
COLOR_SIDEBAR    = "#212F3C"   # Sidebar dark
COLOR_WHITE      = "#FFFFFF"
COLOR_SUCCESS    = "#1E8449"
COLOR_DANGER     = "#C0392B"
COLOR_WARNING    = "#D68910"
COLOR_INFO       = "#1A5276"
COLOR_TEXT_DARK  = "#1C2833"
COLOR_TEXT_LIGHT = "#717D7E"
COLOR_CARD       = "#FFFFFF"
COLOR_BORDER     = "#D5D8DC"

# ── Fonts ─────────────────────────────────────────────────────
FONT_HEADING  = ("Helvetica", 20, "bold")
FONT_SUBHEAD  = ("Helvetica", 14, "bold")
FONT_NORMAL   = ("Helvetica", 11)
FONT_SMALL    = ("Helvetica", 9)
FONT_BUTTON   = ("Helvetica", 11, "bold")
FONT_LABEL    = ("Helvetica", 10)

# ── Map & Distance settings ───────────────────────────────────
ORS_API_KEY    = "eyJvcmciOiI1YjNjZTM1OTc4NTExMTAwMDFjZjYyNDgiLCJpZCI6Ijc0MjM5MTE0OGE2MDQzMTg4NTNkYjk1YmY1MDI2YjVhIiwiaCI6Im11cm11cjY0In0="   # OpenRouteService API key
MAP_DEFAULT_LAT = 27.7172               # Kathmandu centre
MAP_DEFAULT_LNG = 85.3240
MAP_DEFAULT_ZOOM = 13
