import os
from flask import Flask, render_template, request
import requests
from datetime import datetime, timedelta
from dotenv import load_dotenv

load_dotenv()

app = Flask(__name__)
API_KEY = os.getenv("WEATHER_API_KEY")

def convert_to_datetime(timestamp_str):
    """Convert OpenWeatherMap timestamp string to datetime object"""
    try:
        return datetime.strptime(timestamp_str, "%Y-%m-%d %H:%M:%S")
    except (ValueError, TypeError):
        return None

# Get current weather
def get_weather_data(city):
    url = f"https://api.openweathermap.org/data/2.5/weather?q={city}&units=metric&appid={API_KEY}"
    try:
        response = requests.get(url)
        data = response.json()

        if response.status_code != 200 or "main" not in data:
            return {"error": "City not found or API error"}

        weather = {
            "city": data["name"],
            "temperature": round(data["main"]["temp"], 1),
            "description": data["weather"][0]["description"],
            "humidity": data["main"]["humidity"],
            "wind": round(data["wind"]["speed"], 1),
            "lat": data["coord"]["lat"],
            "lon": data["coord"]["lon"],
        }
        return {"weather": weather}
    except Exception as e:
        return {"error": str(e)}

# Get 5-day forecast
def get_forecast_data(city):
    url = f"https://api.openweathermap.org/data/2.5/forecast?q={city}&units=metric&appid={API_KEY}"
    try:
        response = requests.get(url)
        data = response.json()

        if response.status_code != 200 or "list" not in data:
            return {"error": "Forecast data not available"}

        forecast_data = []
        for item in data["list"]:
            timestamp = convert_to_datetime(item["dt_txt"])
            forecast = {
                "timestamp": timestamp,
                "date_str": timestamp.strftime("%Y-%m-%d") if timestamp else item["dt_txt"].split()[0],
                "temperature": round(item["main"]["temp"], 1),
                "feels_like": round(item["main"]["feels_like"], 1),
                "description": item["weather"][0]["description"],
                "humidity": item["main"]["humidity"],
                "wind": round(item["wind"]["speed"], 1),
                "pressure": item["main"]["pressure"],
                "visibility": item.get("visibility", 10000)  # Default to 10km if not available
            }
            forecast_data.append(forecast)

        city_info = {
            "name": data["city"]["name"],
            "country": data["city"]["country"],
            "sunrise": datetime.fromtimestamp(data["city"]["sunrise"]),
            "sunset": datetime.fromtimestamp(data["city"]["sunset"])
        }

        return {"forecast": forecast_data, "city": city_info}
    except Exception as e:
        return {"error": str(e)}
    
@app.route("/", methods=["GET", "POST"])
def index():
    weather = None
    error = None

    if request.method == "POST":
        city = request.form.get("city")
        result = get_weather_data(city)

        if "error" in result:
            error = result["error"]
        else:
            weather = result["weather"]

    return render_template("index.html", weather=weather, error=error)

@app.route("/forecast/<city>")
def forecast(city):
    result = get_forecast_data(city)
    
    if "error" in result:
        return render_template("forecast.html", 
                            error=result["error"], 
                            forecast=None, 
                            city=None)
    
    return render_template('forecast.html',
                         now=datetime.now(),
                         city=result.get("city", {}),
                         forecast=result.get("forecast", []))

if __name__ == "__main__":
    app.run(debug=True)
