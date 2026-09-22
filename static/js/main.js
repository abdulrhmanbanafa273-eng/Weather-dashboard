const form = document.getElementById("search-form");
const cityInput = document.getElementById("city-input");
const searchButton = form.querySelector("button");
const loadingMessage = document.getElementById("loading-message");
const errorMessage = document.getElementById("error-message");
const emptyState = document.getElementById("empty-state");
const weatherResult = document.getElementById("weather-result");
const forecastSection = document.getElementById("forecast");
const forecastCards = document.getElementById("forecast-cards");
const unitButtons = document.querySelectorAll(".unit-toggle button");
const recentSection = document.getElementById("recent-searches");
const recentList = document.getElementById("recent-list");

const RECENT_SEARCHES_KEY = "recentSearches";
const MAX_RECENT_SEARCHES = 5;

// The backend always returns Celsius; we convert in the browser so switching
// units doesn't need another API call.
let currentUnit = localStorage.getItem("unit") === "fahrenheit" ? "fahrenheit" : "celsius";
let lastWeather = null;
let lastForecast = null;

updateUnitButtons();
renderRecentSearches();

unitButtons.forEach((button) => {
    button.addEventListener("click", () => setUnit(button.dataset.unit));
});

document.getElementById("clear-recent").addEventListener("click", () => {
    localStorage.removeItem(RECENT_SEARCHES_KEY);
    renderRecentSearches();
});

form.addEventListener("submit", (event) => {
    event.preventDefault();
    const city = cityInput.value.trim();
    if (!city) {
        return;
    }
    fetchWeather(city);
});

async function fetchWeather(city) {
    hide(emptyState);
    hide(errorMessage);
    hide(weatherResult);
    hide(forecastSection);
    show(loadingMessage);
    searchButton.disabled = true;

    const query = encodeURIComponent(city);

    try {
        const [weather, forecast] = await Promise.all([
            getJson(`/api/weather?city=${query}`),
            getJson(`/api/forecast?city=${query}`),
        ]);

        lastWeather = weather;
        lastForecast = forecast;
        renderWeather(weather);
        renderForecast(forecast);
        saveRecentSearch(weather.city);
    } catch (error) {
        showError(error.message);
    } finally {
        hide(loadingMessage);
        searchButton.disabled = false;
    }
}

async function getJson(url) {
    let response;
    try {
        response = await fetch(url);
    } catch (error) {
        throw new Error("Could not reach the server. Check your connection and try again.");
    }

    const data = await response.json();
    if (!response.ok) {
        throw new Error(data.error || "Something went wrong. Please try again.");
    }
    return data;
}

function loadRecentSearches() {
    try {
        const saved = JSON.parse(localStorage.getItem(RECENT_SEARCHES_KEY));
        return Array.isArray(saved) ? saved.filter((city) => typeof city === "string") : [];
    } catch (error) {
        return [];
    }
}

function saveRecentSearch(city) {
    const others = loadRecentSearches().filter((saved) => saved.toLowerCase() !== city.toLowerCase());
    const updated = [city, ...others].slice(0, MAX_RECENT_SEARCHES);
    localStorage.setItem(RECENT_SEARCHES_KEY, JSON.stringify(updated));
    renderRecentSearches();
}

function renderRecentSearches() {
    const cities = loadRecentSearches();

    const items = cities.map((city) => {
        const button = document.createElement("button");
        button.type = "button";
        button.textContent = city;
        button.addEventListener("click", () => {
            cityInput.value = city;
            fetchWeather(city);
        });

        const item = document.createElement("li");
        item.append(button);
        return item;
    });

    recentList.replaceChildren(...items);
    recentSection.classList.toggle("hidden", cities.length === 0);
}

function setUnit(unit) {
    currentUnit = unit;
    localStorage.setItem("unit", unit);
    updateUnitButtons();

    if (lastWeather) {
        renderWeather(lastWeather);
        renderForecast(lastForecast);
    }
}

function updateUnitButtons() {
    unitButtons.forEach((button) => {
        const isActive = button.dataset.unit === currentUnit;
        button.classList.toggle("active", isActive);
        button.setAttribute("aria-pressed", String(isActive));
    });
}

function convertTemperature(celsius) {
    const value = currentUnit === "fahrenheit" ? (celsius * 9) / 5 + 32 : celsius;
    return Math.round(value);
}

function formatTemperature(celsius) {
    const symbol = currentUnit === "fahrenheit" ? "°F" : "°C";
    return `${convertTemperature(celsius)}${symbol}`;
}

function iconUrl(iconCode) {
    return `https://openweathermap.org/img/wn/${iconCode}@2x.png`;
}

function renderWeather(data) {
    document.getElementById("location").textContent = `${data.city}, ${data.country}`;
    document.getElementById("local-time").textContent = `Local time: ${data.local_time}`;

    const icon = document.getElementById("weather-icon");
    icon.src = iconUrl(data.icon);
    icon.alt = data.condition;

    document.getElementById("temperature").textContent = formatTemperature(data.temperature);
    document.getElementById("feels-like").textContent = `Feels like ${formatTemperature(data.feels_like)}`;
    document.getElementById("condition").textContent = data.condition;
    document.getElementById("humidity").textContent = `${data.humidity}%`;
    document.getElementById("wind").textContent = `${data.wind_speed} m/s`;
    document.getElementById("pressure").textContent = `${data.pressure} hPa`;

    const visibilityKm = data.visibility != null ? `${(data.visibility / 1000).toFixed(1)} km` : "N/A";
    document.getElementById("visibility").textContent = visibilityKm;

    document.getElementById("sunrise").textContent = data.sunrise;
    document.getElementById("sunset").textContent = data.sunset;

    show(weatherResult);
}

function renderForecast(days) {
    const cards = days.map((day, index) => createForecastCard(day, index === 0));
    forecastCards.replaceChildren(...cards);
    show(forecastSection);
}

function createForecastCard(day, isToday) {
    const card = document.createElement("div");
    card.className = "forecast-card";

    const dayName = document.createElement("p");
    dayName.className = "forecast-day";
    dayName.textContent = isToday ? "Today" : day.day_name;

    const icon = document.createElement("img");
    icon.src = iconUrl(day.icon);
    icon.alt = day.condition;

    const temperatures = document.createElement("p");
    temperatures.className = "forecast-temps";
    temperatures.textContent = `${convertTemperature(day.temp_max)}° / ${convertTemperature(day.temp_min)}°`;

    card.append(dayName, icon, temperatures);
    return card;
}

function showError(message) {
    errorMessage.textContent = message;
    show(errorMessage);
}

function hide(element) {
    element.classList.add("hidden");
}

function show(element) {
    element.classList.remove("hidden");
}
