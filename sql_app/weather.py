from dotenv import load_dotenv
import time
import requests
import os

load_dotenv()

WEATHER_API = os.getenv("WEATHER_API")

LATITUDE = 37.488545 # 개포동의 위도
LONGITUDE = 127.065408 # 개포동의 경도

def get_weather():
    current_time = time.time()
    
    if hasattr(get_weather, 'last_call_time') and current_time - get_weather.last_call_time < 43200: # 12시간 = 43200초
        return get_weather.cached_result
        
    url = f"https://api.openweathermap.org/data/2.5/onecall?lat={LATITUDE}&lon={LONGITUDE}&exclude=minutely,hourly,alerts&appid={WEATHER_API}"

    response = requests.get(url)

    if response.status_code == 200:
        data = response.json()
        rain_probability = data['daily'][0]['pop'] * 100 # 오늘의 강수확률 (비율을 백분율로 변환)
        get_weather.last_call_time = current_time
        get_weather.cached_result = rain_probability
        return rain_probability
    else:
        return None