# Project Requirements & Feature List

## Goal
A responsive web app where a user searches for a city and sees its current weather
and a short forecast. Built to demonstrate a full, realistic development workflow
(frontend, backend, API integration, Git/GitHub, testing) for a portfolio.

## Functional requirements

### Search
- User can type a city name and submit a search
- Invalid or unknown city names show a clear error message, not a crash
- Empty search input is rejected before hitting the API

### Current weather (per city)
- Temperature (and "feels like")
- Weather condition (e.g. "Clear", "Rain") with icon
- Humidity
- Wind speed
- Atmospheric pressure
- Visibility
- Sunrise / sunset time
- Location name and local time

### Forecast
- 5-day forecast, one card per day

### UI/UX
- Responsive layout: desktop, tablet, mobile
- Loading state while a request is in flight
- Empty state before any search has been made
- Celsius/Fahrenheit toggle
- Recent searches (if it stays simple)

### Reliability
- Missing API key is caught and reported with a clear error, not a stack trace
- Weather API errors (timeout, rate limit, 5xx) are caught and shown to the user
- No API key or secret is ever exposed to the browser or committed to Git

## Non-functional requirements
- Vanilla HTML/CSS/JS on the frontend, no build tooling
- Python + Flask backend
- Small, readable functions; no single file should try to do everything
- Automated tests for the backend logic that matters (API parsing, error handling, routes)

## Out of scope (for this project)
- User accounts / authentication
- Persisting search history server-side (SQLite is not needed for this app's scope)
- Multi-language support

## Milestones
1. **Week 1** – Project scaffolding, Flask app runs locally, repo on GitHub
2. **Week 2** – Real weather API integration, current-conditions display, error handling
3. **Week 3** – Forecast, responsive UI, unit toggle, polish
4. **Week 4** – Tests, security/cleanup pass, final documentation
