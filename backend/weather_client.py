import requests
import logging
import os


logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')


class WeatherClient:
    def __init__(self):
        self.api_key = os.getenv("OPEN_WEATHER_API_KEY")
        if not self.api_key:
            logging.error("API key for OpenWeather not found in environment variables.")
            raise ValueError("API key for OpenWeather is required and not set.")
    
    def get_weather(self, city: str):
        if not city:
            logging.warning("City parameter is empty.")
            return {"error": "City parameter is required"}

        url = f"https://api.openweathermap.org/data/2.5/weather?q={city}&appid={self.api_key}&units=metric"

        logging.info(f"Requesting weather data for city: {city}")
        response = requests.get(url)
        
        weather_data = response.json()

        if response.status_code != 200:
            error_message = weather_data.get("message", "Unknown error")
            logging.error(f"Error from API: {error_message}")
            return {"error": error_message}

        logging.info(f"Weather data retrieved successfully for {city}.")
        return weather_data

