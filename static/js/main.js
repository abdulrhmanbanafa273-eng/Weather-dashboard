const form = document.getElementById("search-form");
const cityInput = document.getElementById("city-input");
const errorMessage = document.getElementById("error-message");
const weatherResult = document.getElementById("weather-result");

form.addEventListener("submit", (event) => {
    event.preventDefault();
    const city = cityInput.value.trim();
    if (!city) {
        return;
    }
    fetchWeather(city);
});

async function fetchWeather(city) {
    hide(errorMessage);
    hide(weatherResult);

    try {
        const response = await fetch(`/api/weather?city=${encodeURIComponent(city)}`);
        const data = await response.json();

        if (!response.ok) {
            showError(data.error || "Something went wrong. Please try again.");
            return;
        }

        renderWeather(data);
    } catch (error) {
        showError("Could not reach the server. Check your connection and try again.");
    }
}

function renderWeather(data) {
    document.getElementById("location").textContent = `${data.city}, ${data.country}`;
    document.getElementById("local-time").textContent = `Local time: ${data.local_time}`;

    const icon = document.getElementById("weather-icon");
    icon.src = `https://openweathermap.org/img/wn/${data.icon}@2x.png`;
    icon.alt = data.condition;

    document.getElementById("temperature").textContent = `${Math.round(data.temperature)}°C`;
    document.getElementById("feels-like").textContent = `Feels like ${Math.round(data.feels_like)}°C`;
    document.getElementById("condition").textContent = data.condition;
    document.getElementById("humidity").textContent = `Humidity: ${data.humidity}%`;
    document.getElementById("wind").textContent = `Wind: ${data.wind_speed} m/s`;
    document.getElementById("pressure").textContent = `Pressure: ${data.pressure} hPa`;

    const visibilityKm = data.visibility != null ? (data.visibility / 1000).toFixed(1) : "N/A";
    document.getElementById("visibility").textContent = `Visibility: ${visibilityKm} km`;

    document.getElementById("sunrise").textContent = `Sunrise: ${data.sunrise}`;
    document.getElementById("sunset").textContent = `Sunset: ${data.sunset}`;

    show(weatherResult);
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
