from unittest.mock import patch

from app.weather_service import CityNotFoundError, MissingAPIKeyError, WeatherAPIError


def test_index_returns_200(client):
    response = client.get("/")
    assert response.status_code == 200
    assert b"Weather Dashboard" in response.data


def test_api_weather_requires_city(client):
    response = client.get("/api/weather?city=")
    assert response.status_code == 400
    assert response.get_json()["error"]


def test_api_weather_returns_data_on_success(client):
    fake_weather = {"city": "Dubai", "temperature": 36.0}
    with patch("app.routes.get_current_weather", return_value=fake_weather) as mock_get:
        response = client.get("/api/weather?city=Dubai")

    mock_get.assert_called_once_with("Dubai")
    assert response.status_code == 200
    assert response.get_json() == fake_weather


def test_api_weather_city_not_found_returns_404(client):
    with patch(
        "app.routes.get_current_weather",
        side_effect=CityNotFoundError('City "X" was not found.'),
    ):
        response = client.get("/api/weather?city=X")

    assert response.status_code == 404
    assert "not found" in response.get_json()["error"]


def test_api_weather_missing_api_key_returns_500(client):
    with patch("app.routes.get_current_weather", side_effect=MissingAPIKeyError("no key")):
        response = client.get("/api/weather?city=Dubai")

    assert response.status_code == 500


def test_api_weather_upstream_failure_returns_502(client):
    with patch("app.routes.get_current_weather", side_effect=WeatherAPIError("boom")):
        response = client.get("/api/weather?city=Dubai")

    assert response.status_code == 502


def test_api_forecast_requires_city(client):
    response = client.get("/api/forecast?city=")
    assert response.status_code == 400


def test_api_forecast_returns_data_on_success(client):
    fake_forecast = [{"date": "2026-01-01", "temp_max": 30}]
    with patch("app.routes.get_forecast", return_value=fake_forecast) as mock_get:
        response = client.get("/api/forecast?city=Dubai")

    mock_get.assert_called_once_with("Dubai")
    assert response.status_code == 200
    assert response.get_json() == fake_forecast


def test_api_forecast_city_not_found_returns_404(client):
    with patch(
        "app.routes.get_forecast",
        side_effect=CityNotFoundError('City "X" was not found.'),
    ):
        response = client.get("/api/forecast?city=X")

    assert response.status_code == 404
