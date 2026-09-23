# Weather Dashboard

A responsive web app for looking up the current weather and a 5-day forecast for any
city. Built as a portfolio project to practice a real frontend/backend/API workflow,
from planning through Git branches, pull requests, tests, and a security pass.

## Overview
Type a city name and get back current conditions (temperature, feels-like, condition,
humidity, wind, pressure, visibility, sunrise/sunset, local time) plus a 5-day forecast.
Switch between Celsius and Fahrenheit, and jump back to a recent search with one click.

## Features
- [x] City search with a REST API backing it
- [x] Current conditions: temperature, feels-like, condition + icon, humidity, wind,
      pressure, visibility, sunrise/sunset, local time
- [x] 5-day forecast, grouped from the API's raw 3-hour data
- [x] Responsive layout (desktop / tablet / mobile)
- [x] Celsius/Fahrenheit toggle (persisted across reloads)
- [x] Recent searches (last 5, stored in the browser, click to re-search)
- [x] Loading state and empty state
- [x] Error handling for invalid cities, missing API key, and upstream API failures
- [x] Automated backend tests

See [REQUIREMENTS.md](REQUIREMENTS.md) for the original planning doc and scope.

## Technologies
- **Frontend:** HTML5, CSS3, vanilla JavaScript (no frameworks, no build step)
- **Backend:** Python, Flask
- **Testing:** pytest, with `unittest.mock` for the HTTP layer
- **API:** [OpenWeatherMap](https://openweathermap.org/api)

## Architecture
```
Browser (fetch)  -->  Flask routes (/api/weather, /api/forecast)
                              |
                              v
                     app/weather_service.py
                              |
                              v
                    OpenWeatherMap REST API
                              |
                              v
                 parsed into a small JSON shape  -->  Browser renders it
```
The frontend never talks to OpenWeatherMap directly and never sees the API key — it
only calls our own two routes, which do the external request server-side and return a
trimmed-down JSON response. `app/weather_service.py` owns all the OpenWeatherMap-specific
logic (URLs, error codes, response shape); `app/routes.py` only handles the web-facing
concerns (validating `?city=`, mapping exceptions to HTTP status codes).

## Installation

```bash
git clone https://github.com/abdulrhmanbanafa273-eng/Weather-dashboard.git
cd Weather-dashboard
python -m venv venv
```

Activate the virtual environment:
```bash
venv\Scripts\activate       # Windows
source venv/bin/activate    # macOS / Linux
```

Install dependencies:
```bash
pip install -r requirements.txt          # just to run the app
pip install -r requirements-dev.txt      # to also run the tests (includes the above)
```

## Environment Variables
Copy `.env.example` to `.env` and fill in your own values — `.env` is git-ignored and
is never committed:

```bash
copy .env.example .env      # Windows
cp .env.example .env        # macOS / Linux
```

| Variable | Description |
|---|---|
| `WEATHER_API_KEY` | Free API key from [openweathermap.org/api](https://openweathermap.org/api) |
| `FLASK_DEBUG` | `True` for local development only. Defaults to `False` if unset — never leave this on in production |

## Running Locally
```bash
python run.py
```
Then open http://127.0.0.1:5000 in your browser.

## API
This project uses [OpenWeatherMap](https://openweathermap.org/api):
- **Current Weather Data** (`/data/2.5/weather`) — temperature, feels-like, condition,
  icon, humidity, wind, pressure, visibility, sunrise/sunset, all in one response
- **5 Day / 3 Hour Forecast** (`/data/2.5/forecast`) — grouped into 5 daily cards by the
  backend, since the API itself only returns 3-hour intervals

Chosen because its free tier requires no credit card, covers nearly every field this
app needs from a single request, and is one of the most widely used weather APIs.

## Testing
```bash
pytest -v
```
19 tests covering:
- `app/weather_service.py`: parsing a successful response, an invalid city (404), a
  rejected API key (401), a generic upstream error (500), a request timeout, a
  connection failure (and that its raw exception text never leaks to the user), a
  missing `WEATHER_API_KEY`, and the forecast grouping/aggregation logic (5-day cutoff,
  high/low spanning multiple 3-hour entries)
- `app/routes.py`: the homepage, empty-city validation, and both endpoints returning
  the right status code and body for success, not-found, missing-key, and upstream-error
  cases

All HTTP calls are mocked in tests — nothing here calls the real OpenWeatherMap API, so
the suite runs the same with or without a valid key.

## Screenshots
Not included in this repo yet. Run the app locally (see above) and search a city to see
the current layout — desktop shows the weather card and forecast side by side, tablet
and phone stack everything and shrink the forecast cards to fit five across.

## Future Improvements
- "Use my location" via the browser's geolocation API
- A small SQLite cache so repeated searches for the same city within a few minutes
  don't re-hit the external API
- Dark mode
- Hourly forecast view, not just daily

## What I Learned
- Structuring a Flask app with an application factory (`create_app()`) and a
  blueprint, instead of one big file
- Keeping all third-party API logic (URLs, error codes, response parsing) in one
  module (`weather_service.py`) so the routes only deal with HTTP concerns
- Why `.env` / `.env.example` matters: the app fails safely with a clear error when
  `WEATHER_API_KEY` is missing, instead of leaking that requirement through a crash
- Mocking `requests.get` with `unittest.mock.patch` to test error handling (timeouts,
  bad status codes) without depending on the real API being reachable or slow
- Real Git workflow: feature branches off `develop`, pull requests instead of direct
  pushes, and resolving an actual merge conflict (two branches changed the same CSS/HTML
  at once) rather than a staged one
- Debug mode should never be hardcoded — it's an environment variable that defaults to
  off, since leaving Werkzeug's debugger on in production is a real vulnerability

## License
MIT
