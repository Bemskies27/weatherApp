async function fetchWeather() {
  const city = document.getElementById("cityInput").value || "Lagos";
  const response = await fetch(`/api/weather?city=${city}`);
  const data = await response.json();
  const container = document.getElementById("weatherData");

  if (data.error) {
    container.innerHTML = `<p class="error">⚠️ ${data.error}</p>`;
    return;
  }

  const icon = data.icon
    ? `<img src="https://openweathermap.org/img/wn/${data.icon}@2x.png" alt="Weather Icon">`
    : '';

  container.innerHTML = `
    <h2>📍 ${city.toUpperCase()}</h2>
    ${icon}
    <p><strong>Temperature:</strong> ${data.temperature}°C</p>
    <p><strong>Humidity:</strong> ${data.humidity}%</p>
    <p><strong>Wind Speed:</strong> ${data.windSpeed} m/s</p>
    <p><strong>Condition:</strong> ${data.conditions}</p>
    <p><strong>Time:</strong> ${new Date(data.timestamp * 1000).toLocaleString()}</p>
  `;

  updateMap(data.coordinates.lat, data.coordinates.lon);
}

let map;

function updateMap(lat, lon) {
  if (!map) {
    map = L.map("map").setView([lat, lon], 10);
    L.tileLayer("https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png", {
      attribution: "© OpenStreetMap contributors"
    }).addTo(map);
  } else {
    map.setView([lat, lon], 10);
  }

  L.marker([lat, lon]).addTo(map);
}
