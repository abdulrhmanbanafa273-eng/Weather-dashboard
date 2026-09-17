# Weather Dashboard

> Status: Week 1 — project scaffolding only. Search and weather data are not implemented yet.

## Overview
A responsive web app for looking up the current weather and short-term forecast for any
city. Built as a portfolio project demonstrating a full frontend/backend/API workflow.

## Features
- [ ] City search
- [ ] Current conditions (temperature, humidity, wind, pressure, visibility, sunrise/sunset)
- [ ] 5-day forecast
- [ ] Responsive layout (desktop/tablet/mobile)
- [ ] Celsius/Fahrenheit toggle
- [ ] Error handling for invalid cities and API failures

See [REQUIREMENTS.md](REQUIREMENTS.md) for the full feature list and scope.

## Technologies
- **Frontend:** HTML5, CSS3, vanilla JavaScript
- **Backend:** Python, Flask
- **API:** TBD — chosen and documented in Week 2

## Architecture
```
Browser  -->  Flask routes  -->  Weather API
   ^                                  |
   |__________ JSON response _________|
```
(Details filled in as the app is built.)

## Installation

```bash
git clone <repo-url>
cd weather-dashboard
python -m venv venv
venv\Scripts\activate        # Windows
pip install -r requirements.txt
```

## Environment Variables
Copy `.env.example` to `.env` and fill in your own values:

```bash
copy .env.example .env
```

| Variable | Description |
|---|---|
| `WEATHER_API_KEY` | API key for the weather provider |
| `FLASK_DEBUG` | `True` for local development only |

## Running Locally
```bash
python run.py
```
Then open http://127.0.0.1:5000 in your browser.

## API
Documented once the provider is chosen in Week 2.

## Testing
No automated tests yet — added in Week 4.

## Screenshots
Added once the UI is built out.

## Future Improvements
TBD.

## What I Learned
TBD — written at the end of the project.

## License
MIT
