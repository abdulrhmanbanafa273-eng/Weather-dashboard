import os
from datetime import datetime, timedelta, timezone

import requests

BASE_URL = "https://api.openweathermap.org/data/2.5"
REQUEST_TIMEOUT_SECONDS = 5
FORECAST_DAYS = 5


class MissingAPIKeyError(Exception):
    """Raised when the WEATHER_API_KEY environment variable is not set."""


class CityNotFoundError(Exception):
    """Raised when the weather API can't find the requested city."""


class WeatherAPIError(Exception):
    """Raised when the weather API request fails for any reason other than an unknown city."""


def get_current_weather(city, units="metric"):
    """Fetch and parse current weather conditions for a city from OpenWeatherMap."""
    data = _fetch_from_api("weather", city, units)
    return _parse_current_weather(data)


def get_forecast(city, units="metric"):
    """Fetch the forecast for a city and summarize it as one entry per day."""
    data = _fetch_from_api("forecast", city, units)
    return _parse_forecast(data)


def _fetch_from_api(endpoint, city, units):
    """Call an OpenWeatherMap endpoint and turn failures into our own exceptions."""
    api_key = _get_api_key()

    try:
        response = requests.get(
            f"{BASE_URL}/{endpoint}",
            params={"q": city, "appid": api_key, "units": units},
            timeout=REQUEST_TIMEOUT_SECONDS,
        )
    except requests.exceptions.RequestException as error:
        raise WeatherAPIError(f"Could not reach the weather service: {error}") from error

    if response.status_code == 404:
        raise CityNotFoundError(f'City "{city}" was not found.')

    if response.status_code == 401:
        raise WeatherAPIError("The weather API rejected the API key.")

    if not response.ok:
        raise WeatherAPIError(f"The weather API returned status {response.status_code}.")

    return response.json()


def _get_api_key():
    api_key = os.environ.get("WEATHER_API_KEY")
    if not api_key:
        raise MissingAPIKeyError("WEATHER_API_KEY is not set. Add it to your .env file.")
    return api_key


def _parse_current_weather(data):
    """Pull out the fields the frontend needs from OpenWeatherMap's raw response."""
    offset_seconds = data["timezone"]

    return {
        "city": data["name"],
        "country": data["sys"].get("country"),
        "temperature": data["main"]["temp"],
        "feels_like": data["main"]["feels_like"],
        "condition": data["weather"][0]["description"].title(),
        "icon": data["weather"][0]["icon"],
        "humidity": data["main"]["humidity"],
        "wind_speed": data["wind"]["speed"],
        "pressure": data["main"]["pressure"],
        "visibility": data.get("visibility"),
        "sunrise": _format_local_time(data["sys"]["sunrise"], offset_seconds),
        "sunset": _format_local_time(data["sys"]["sunset"], offset_seconds),
        "local_time": _format_local_time(data["dt"], offset_seconds),
    }


def _parse_forecast(data):
    """Group OpenWeatherMap's 3-hour forecast entries into one summary per local day."""
    city_timezone = timezone(timedelta(seconds=data["city"]["timezone"]))

    entries_by_date = {}
    for entry in data["list"]:
        local_time = datetime.fromtimestamp(entry["dt"], tz=city_timezone)
        entries_by_date.setdefault(local_time.date(), []).append((local_time, entry))

    # Dates are inserted in chronological order. The first day is today, so its
    # high/low only covers the hours that are still to come.
    days = list(entries_by_date.items())[:FORECAST_DAYS]
    return [_summarize_day(date, entries) for date, entries in days]


def _summarize_day(date, entries):
    """Build one forecast card: overall high/low plus the condition closest to midday."""
    midday_entry = min(entries, key=lambda item: abs(item[0].hour - 12))[1]

    return {
        "date": date.isoformat(),
        "day_name": date.strftime("%a"),
        "temp_min": min(entry["main"]["temp_min"] for _, entry in entries),
        "temp_max": max(entry["main"]["temp_max"] for _, entry in entries),
        "condition": midday_entry["weather"][0]["description"].title(),
        "icon": midday_entry["weather"][0]["icon"],
    }


def _format_local_time(unix_timestamp, offset_seconds):
    """Convert a UTC unix timestamp to a human-readable local time using the city's UTC offset."""
    city_timezone = timezone(timedelta(seconds=offset_seconds))
    return datetime.fromtimestamp(unix_timestamp, tz=city_timezone).strftime("%I:%M %p")
