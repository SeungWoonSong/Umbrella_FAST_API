from dotenv import load_dotenv
from .schemas import WeatherCondition
import time
import requests
import os

load_dotenv()

WEATHER_API = os.getenv("WEATHER_API")

LATITUDE = 37.488545  # 개포동의 위도
LONGITUDE = 127.065408  # 개포동의 경도


def get_uv_index_category(uv_index):
    if uv_index < 3:
        return "낮음"
    elif 3 <= uv_index < 6:
        return "보통"
    elif 6 <= uv_index < 8:
        return "높음"
    elif 8 <= uv_index < 11:
        return "매우 높음"
    else:
        return "위험"


def get_weather():
    current_time = time.time()

    if (
        hasattr(get_weather, "last_call_time")
        and current_time - get_weather.last_call_time < 43200
    ):  # 12시간 = 43200초
        return get_weather.cached_result

    url = f"https://api.openweathermap.org/data/2.5/onecall?lat={LATITUDE}&lon={LONGITUDE}&exclude=minutely,hourly,alerts&appid={WEATHER_API}"

    response = requests.get(url)

    if response.status_code == 200:
        data = response.json()
        rain_probability = data["daily"][0]["pop"] * 100  # 오늘의 강수확률 (비율을 백분율로 변환)
        uv_index = data["daily"][0]["uvi"]  # 오늘의 자외선 지수
        weather_condition = WeatherCondition(
            rain_probability=rain_probability,
            uv_index=uv_index,
            uv_index_category=get_uv_index_category(uv_index),
        )
        get_weather.last_call_time = current_time
        get_weather.cached_result = weather_condition
        return weather_condition
    else:
        return None
