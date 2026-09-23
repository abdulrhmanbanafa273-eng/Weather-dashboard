from datetime import datetime, timezone
from unittest.mock import Mock, patch

import pytest
import requests

from app.weather_service import (
    CityNotFoundError,
    MissingAPIKeyError,
    WeatherAPIError,
    get_current_weather,
    get_forecast,
)

CURRENT_WEATHER_JSON = {
    "name": "Dubai",
    "sys": {"country": "AE", "sunrise": 1700000000, "sunset": 1700040000},
    "main": {"temp": 36.0, "feels_like": 38.0, "humidity": 36, "pressure": 1010},
    "weather": [{"description": "clear sky", "icon": "01d"}],
    "wind": {"speed": 2.06},
    "visibility": 10000,
    "timezone": 0,
    "dt": 1700010000,
}


def make_response(status_code, json_data):
    response = Mock()
    response.status_code = status_code
    response.ok = status_code == 200
    response.json.return_value = json_data
    return response


def make_forecast_entry(dt, temp_min, temp_max, description="clear sky", icon="01d"):
    return {
        "dt": int(dt.timestamp()),
        "main": {"temp_min": temp_min, "temp_max": temp_max},
        "weather": [{"description": description, "icon": icon}],
    }


def test_get_current_weather_parses_expected_fields(monkeypatch):
    monkeypatch.setenv("WEATHER_API_KEY", "test-key")
    with patch("app.weather_service.requests.get", return_value=make_response(200, CURRENT_WEATHER_JSON)):
        weather = get_current_weather("Dubai")

    assert weather["city"] == "Dubai"
    assert weather["country"] == "AE"
    assert weather["temperature"] == 36.0
    assert weather["feels_like"] == 38.0
    assert weather["condition"] == "Clear Sky"
    assert weather["icon"] == "01d"
    assert weather["humidity"] == 36
    assert weather["wind_speed"] == 2.06
    assert weather["pressure"] == 1010
    assert weather["visibility"] == 10000
    assert weather["sunrise"]
    assert weather["sunset"]
    assert weather["local_time"]


def test_get_current_weather_missing_api_key(monkeypatch):
    monkeypatch.delenv("WEATHER_API_KEY", raising=False)

    with pytest.raises(MissingAPIKeyError):
        get_current_weather("Dubai")


def test_get_current_weather_invalid_city(monkeypatch):
    monkeypatch.setenv("WEATHER_API_KEY", "test-key")
    with patch("app.weather_service.requests.get", return_value=make_response(404, {})):
        with pytest.raises(CityNotFoundError):
            get_current_weather("Nonexistentcityxyz")


def test_get_current_weather_rejected_api_key(monkeypatch):
    monkeypatch.setenv("WEATHER_API_KEY", "bad-key")
    with patch("app.weather_service.requests.get", return_value=make_response(401, {})):
        with pytest.raises(WeatherAPIError):
            get_current_weather("Dubai")


def test_get_current_weather_server_error(monkeypatch):
    monkeypatch.setenv("WEATHER_API_KEY", "test-key")
    with patch("app.weather_service.requests.get", return_value=make_response(500, {})):
        with pytest.raises(WeatherAPIError):
            get_current_weather("Dubai")


def test_get_current_weather_timeout(monkeypatch):
    monkeypatch.setenv("WEATHER_API_KEY", "test-key")
    with patch("app.weather_service.requests.get", side_effect=requests.exceptions.Timeout()):
        with pytest.raises(WeatherAPIError, match="took too long"):
            get_current_weather("Dubai")


def test_get_current_weather_connection_error_hides_details(monkeypatch):
    monkeypatch.setenv("WEATHER_API_KEY", "test-key")
    error = requests.exceptions.ConnectionError(
        "HTTPSConnectionPool(host='api.openweathermap.org', port=443): read timed out"
    )
    with patch("app.weather_service.requests.get", side_effect=error):
        with pytest.raises(WeatherAPIError) as exc_info:
            get_current_weather("Dubai")

    assert "HTTPSConnectionPool" not in str(exc_info.value)


def test_get_forecast_keeps_only_five_days(monkeypatch):
    monkeypatch.setenv("WEATHER_API_KEY", "test-key")

    base = datetime(2026, 1, 1, tzinfo=timezone.utc)
    entries = []
    for day in range(6):  # six days of raw data; only the first five should survive
        for hour in (0, 12, 21):
            entries.append(
                make_forecast_entry(
                    base.replace(day=1 + day, hour=hour),
                    temp_min=10 + day,
                    temp_max=20 + day,
                    description="scattered clouds" if hour == 12 else "clear sky",
                    icon="03d" if hour == 12 else "01n",
                )
            )

    forecast_json = {"city": {"timezone": 0}, "list": entries}

    with patch("app.weather_service.requests.get", return_value=make_response(200, forecast_json)):
        days = get_forecast("Dubai")

    assert len(days) == 5
    assert days[0]["temp_min"] == 10
    assert days[0]["temp_max"] == 20
    assert days[0]["condition"] == "Scattered Clouds"
    assert days[0]["icon"] == "03d"
    assert days[0]["day_name"] == base.replace(day=1).strftime("%a")


def test_get_forecast_high_low_spans_all_entries_in_a_day(monkeypatch):
    monkeypatch.setenv("WEATHER_API_KEY", "test-key")

    day = datetime(2026, 1, 1, tzinfo=timezone.utc)
    entries = [
        make_forecast_entry(day.replace(hour=0), temp_min=12, temp_max=15),
        make_forecast_entry(day.replace(hour=12), temp_min=20, temp_max=28),
        make_forecast_entry(day.replace(hour=21), temp_min=9, temp_max=14),
    ]
    forecast_json = {"city": {"timezone": 0}, "list": entries}

    with patch("app.weather_service.requests.get", return_value=make_response(200, forecast_json)):
        days = get_forecast("Dubai")

    assert days[0]["temp_min"] == 9
    assert days[0]["temp_max"] == 28


def test_get_forecast_invalid_city(monkeypatch):
    monkeypatch.setenv("WEATHER_API_KEY", "test-key")
    with patch("app.weather_service.requests.get", return_value=make_response(404, {})):
        with pytest.raises(CityNotFoundError):
            get_forecast("Nonexistentcityxyz")
