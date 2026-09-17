from flask import Blueprint, jsonify, render_template, request

from app.weather_service import (
    CityNotFoundError,
    MissingAPIKeyError,
    WeatherAPIError,
    get_current_weather,
)

main = Blueprint("main", __name__)


@main.route("/")
def index():
    return render_template("index.html")


@main.route("/api/weather")
def api_weather():
    city = request.args.get("city", "").strip()
    if not city:
        return jsonify({"error": "Please enter a city name."}), 400

    try:
        weather = get_current_weather(city)
    except MissingAPIKeyError:
        return jsonify({"error": "The server is missing a weather API key."}), 500
    except CityNotFoundError:
        return jsonify({"error": f'City "{city}" was not found.'}), 404
    except WeatherAPIError as error:
        return jsonify({"error": str(error)}), 502

    return jsonify(weather)
