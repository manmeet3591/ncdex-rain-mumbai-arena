import requests
from config import OPEN_METEO_ARCHIVE_URL, OPEN_METEO_FORECAST_URL


def fetch_historical_precipitation(lat: float, lon: float, start_date: str, end_date: str) -> list[dict]:
    resp = requests.get(OPEN_METEO_ARCHIVE_URL, params={
        "latitude": lat,
        "longitude": lon,
        "start_date": start_date,
        "end_date": end_date,
        "daily": "precipitation_sum",
        "timezone": "Asia/Kolkata",
    }, timeout=30)
    resp.raise_for_status()
    data = resp.json()
    daily = data.get("daily", {})
    dates = daily.get("time", [])
    values = daily.get("precipitation_sum", [])
    return [{"date": d, "value": v} for d, v in zip(dates, values)]


def fetch_historical_temperature(lat: float, lon: float, start_date: str, end_date: str) -> list[dict]:
    resp = requests.get(OPEN_METEO_ARCHIVE_URL, params={
        "latitude": lat,
        "longitude": lon,
        "start_date": start_date,
        "end_date": end_date,
        "daily": "temperature_2m_max",
        "timezone": "auto",
    }, timeout=30)
    resp.raise_for_status()
    data = resp.json()
    daily = data.get("daily", {})
    dates = daily.get("time", [])
    values = daily.get("temperature_2m_max", [])
    return [{"date": d, "value": v} for d, v in zip(dates, values)]


def fetch_forecast_precipitation(lat: float, lon: float, days: int = 7) -> list[dict]:
    resp = requests.get(OPEN_METEO_FORECAST_URL, params={
        "latitude": lat,
        "longitude": lon,
        "daily": "precipitation_sum",
        "timezone": "Asia/Kolkata",
        "forecast_days": days,
    }, timeout=15)
    resp.raise_for_status()
    data = resp.json()
    daily = data.get("daily", {})
    dates = daily.get("time", [])
    values = daily.get("precipitation_sum", [])
    return [{"date": d, "value": v} for d, v in zip(dates, values)]


def fetch_forecast_temperature(lat: float, lon: float, days: int = 7) -> list[dict]:
    resp = requests.get(OPEN_METEO_FORECAST_URL, params={
        "latitude": lat,
        "longitude": lon,
        "daily": "temperature_2m_max",
        "timezone": "auto",
        "forecast_days": days,
    }, timeout=15)
    resp.raise_for_status()
    data = resp.json()
    daily = data.get("daily", {})
    dates = daily.get("time", [])
    values = daily.get("temperature_2m_max", [])
    return [{"date": d, "value": v} for d, v in zip(dates, values)]
