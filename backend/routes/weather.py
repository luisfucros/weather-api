from fastapi import Depends, APIRouter
from backend import schemas
from backend.utils import oauth2
from backend.weather_client import WeatherClient
from backend.utils.caching import get_cached_data, insert_data
import json

router = APIRouter(
    prefix="/weather",
    tags=['Weather']
)

weather_client = WeatherClient()

@router.get("/{city}")
def get_weather(
    city: str,
    current_user: schemas.UserOut = Depends(oauth2.get_current_user)
):
    cached_data = get_cached_data(city)
    if cached_data:
        return json.loads(cached_data)
    
    weather_data = weather_client.get_weather(city)

    if weather_data.get('cod') == 200:
        insert_data(city, weather_data)
    
    return weather_data
