MUMBAI_LAT = 19.076
MUMBAI_LON = 72.878

OPEN_METEO_ARCHIVE_URL = "https://archive-api.open-meteo.com/v1/archive"
OPEN_METEO_FORECAST_URL = "https://api.open-meteo.com/v1/forecast"

POLYMARKET_EVENTS_URL = "https://gamma-api.polymarket.com/events"

POLYMARKET_CITY_COORDS = {
    "New York City": {"lat": 40.75, "lon": -74.00},
    "NYC": {"lat": 40.75, "lon": -74.00},
    "Chicago": {"lat": 41.88, "lon": -87.63},
    "Atlanta": {"lat": 33.75, "lon": -84.40},
    "Dallas": {"lat": 32.78, "lon": -96.80},
    "Miami": {"lat": 25.76, "lon": -80.20},
    "Seattle": {"lat": 47.61, "lon": -122.33},
    "Toronto": {"lat": 43.65, "lon": -79.38},
    "London": {"lat": 51.51, "lon": -0.13},
    "Paris": {"lat": 48.86, "lon": 2.35},
    "Milan": {"lat": 45.46, "lon": 9.19},
    "Madrid": {"lat": 40.42, "lon": -3.69},
    "Munich": {"lat": 48.14, "lon": 11.58},
    "Warsaw": {"lat": 52.23, "lon": 21.01},
    "Tokyo": {"lat": 35.68, "lon": 139.69},
    "Seoul": {"lat": 37.57, "lon": 126.98},
    "Singapore": {"lat": 1.35, "lon": 103.82},
    "Hong Kong": {"lat": 22.32, "lon": 114.17},
    "Shanghai": {"lat": 31.23, "lon": 121.47},
    "Beijing": {"lat": 39.90, "lon": 116.40},
    "Tel Aviv": {"lat": 32.09, "lon": 34.78},
    "Buenos Aires": {"lat": -34.60, "lon": -58.38},
    "Sao Paulo": {"lat": -23.55, "lon": -46.63},
}

POSITION_SIZE_USD = 10.0
MIN_EDGE_THRESHOLD = 0.10
MAX_POSITIONS_PER_EVENT = 2

NCDEX_SEASON_START_MONTH = 6
NCDEX_SEASON_END_MONTH = 9
NCDEX_ANCHOR_CDR = 2206.7

MARKETS = {
    "rainfall_mumbai": {
        "variable": "precipitation_mm",
        "locations": ["mumbai"],
    },
    "temperature_polymarket": {
        "variable": "temperature_max_c",
        "locations": list(POLYMARKET_CITY_COORDS.keys()),
    },
}

DB_PATH = "arena.db"
