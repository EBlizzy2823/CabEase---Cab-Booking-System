# =============================================================
#  modules/map_utils.py
#  Geocoding, place search, and real road distance calculation
# =============================================================

import requests
import sys, os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import config

HEADERS = {"User-Agent": "TaxiBookingSystem-FYP/1.0 (student project)"}


# ── Place search (returns multiple results) ───────────────────

def search_places(query: str, limit: int = 8) -> list[dict]:
    """
    Searches for places matching the query string in Nepal.
    Returns a list of result dicts with keys:
        display_name, lat, lon
    """
    try:
        url = "https://nominatim.openstreetmap.org/search"
        params = {
            "q"              : query + ", Nepal",
            "format"         : "json",
            "limit"          : limit,
            "countrycodes"   : "np",
            "accept-language": "en",
        }
        resp = requests.get(url, params=params,
                            headers=HEADERS, timeout=10)
        return resp.json() or []
    except Exception as e:
        print(f"[SEARCH ERROR] {e}")
        return []


# ── Geocoding: place name → (lat, lng) ───────────────────────

def geocode_place(place_name: str) -> tuple[float, float] | None:
    """
    Converts a place name into (latitude, longitude).
    Returns None if the place cannot be found.
    """
    try:
        url = "https://nominatim.openstreetmap.org/search"
        params = {
            "q"              : place_name + ", Nepal",
            "format"         : "json",
            "limit"          : 1,
            "countrycodes"   : "np",
            "accept-language": "en",
        }
        resp = requests.get(url, params=params,
                            headers=HEADERS, timeout=10)
        data = resp.json()
        if data:
            return float(data[0]["lat"]), float(data[0]["lon"])
        return None
    except Exception as e:
        print(f"[GEOCODE ERROR] {e}")
        return None


# ── Reverse geocoding: (lat, lng) → place name ───────────────

def reverse_geocode(lat: float, lng: float) -> str:
    """Converts coordinates back to a readable place name."""
    try:
        url = "https://nominatim.openstreetmap.org/reverse"
        params = {"lat": lat, "lon": lng, "format": "json"}
        resp = requests.get(url, params=params,
                            headers=HEADERS, timeout=10)
        data = resp.json()
        addr  = data.get("address", {})
        parts = []
        for key in ("road", "suburb", "city_district",
                    "city", "town", "village"):
            if addr.get(key):
                parts.append(addr[key])
                if len(parts) == 2:
                    break
        return ", ".join(parts) if parts \
            else data.get("display_name", f"{lat:.4f},{lng:.4f}")
    except Exception as e:
        print(f"[REVERSE GEOCODE ERROR] {e}")
        return f"{lat:.4f}, {lng:.4f}"


# ── Real road distance via OpenRouteService ───────────────────

def get_road_distance_km(origin_lat: float, origin_lng: float,
                          dest_lat: float,   dest_lng: float
                          ) -> float:
    """
    Gets the actual driving distance between two GPS points.
    Uses OpenRouteService if an API key is set in config.py,
    otherwise falls back to the Haversine straight-line formula.
    """
    api_key = getattr(config, "ORS_API_KEY", "")
    if api_key and api_key != "PASTE_YOUR_KEY_HERE":
        try:
            url = "https://api.openrouteservice.org/v2/directions/driving-car"
            headers = {
                "Authorization": api_key,
                "Content-Type" : "application/json",
            }
            body = {
                "coordinates": [
                    [origin_lng, origin_lat],
                    [dest_lng,   dest_lat],
                ]
            }
            resp = requests.post(url, json=body,
                                 headers=headers, timeout=12)
            data = resp.json()
            metres = data["routes"][0]["summary"]["distance"]
            return round(metres / 1000, 2)
        except Exception as e:
            print(f"[ORS ERROR] {e} — using Haversine fallback")

    return haversine_km(origin_lat, origin_lng, dest_lat, dest_lng)


# ── Haversine straight-line distance ─────────────────────────

def haversine_km(lat1: float, lng1: float,
                 lat2: float, lng2: float) -> float:
    """Straight-line distance between two GPS points in km."""
    import math
    R    = 6371.0
    dlat = math.radians(lat2 - lat1)
    dlng = math.radians(lng2 - lng1)
    a    = (math.sin(dlat / 2) ** 2 +
            math.cos(math.radians(lat1)) *
            math.cos(math.radians(lat2)) *
            math.sin(dlng / 2) ** 2)
    return round(R * 2 * math.asin(math.sqrt(a)), 2)


# ── Main helper used by the booking form ──────────────────────

def calculate_distance_between_places(pickup: str,
                                       dropoff: str) -> float:
    """
    Geocodes both place names then returns the road distance in km.
    Falls back to 5.0 km if geocoding fails.
    """
    pickup_coords  = geocode_place(pickup)
    dropoff_coords = geocode_place(dropoff)

    if pickup_coords and dropoff_coords:
        dist = get_road_distance_km(
            pickup_coords[0],  pickup_coords[1],
            dropoff_coords[0], dropoff_coords[1]
        )
        return max(dist, 1.0)

    print(f"[DISTANCE] Could not geocode '{pickup}' or '{dropoff}'")
    return 5.0
