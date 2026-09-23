from flask import Blueprint, jsonify, render_template, request

from app.weather_service import (
    CityNotFoundError,
    MissingAPIKeyError,
    WeatherAPIError,
    get_current_weather,
    get_forecast,
)

main = Blueprint("main", __name__)


@main.route("/")
def index():
    return render_template("index.html")


@main.route("/api/weather")
def api_weather():
    return _json_for_city(get_current_weather)


@main.route("/api/forecast")
def api_forecast():
    return _json_for_city(get_forecast)


def _json_for_city(fetch_data):
    """Validate the ?city= parameter, call fetch_data(city), and map failures to JSON errors."""
    city = request.args.get("city", "").strip()
    if not city:
        return jsonify({"error": "Please enter a city name."}), 400

    try:
        data = fetch_data(city)
    except MissingAPIKeyError:
        return jsonify({"error": "The server is missing a weather API key."}), 500
    except CityNotFoundError:
        return jsonify({"error": f'City "{city}" was not found.'}), 404
    except WeatherAPIError as error:
        return jsonify({"error": str(error)}), 502

    return jsonify(data)
