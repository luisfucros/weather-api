import requests
import os


class WeatherClient:
    def __init__(self):
        self._secret_api = os.getenv("OPEN_WEATHER_API_KEY")
    
    def get_weather(self, city: str):
        url = f"https://api.openweathermap.org/data/2.5/weather?q={city}&appid={self._secret_api}&units=metric"

        payload = {}
        headers = {}

        response = requests.request("GET", url, headers=headers, data=payload)

        return response.json()
