from datetime import datetime
import requests
from flask import request
from dotenv import dotenv_values

import logging
logger = logging.getLogger(__name__)

config = dotenv_values(".env")


def get_geocoding(city: str = None):
    key = config["GEOCODE_API_KEY"]
    url = f'https://geocode.maps.co/search?q={city}&api_key={key}'

    response = requests.get(url)

    if response.status_code == 200:
        posts = response.json()
        return posts
    else:
        print('Error:', response.status_code)
        return None


def get_coordinates(city: str = None):
    res = get_geocoding(city)[0]
    return (res['lat'], res['lon'])


def get_point(latitude, longitude):
    url = f'https://api.weather.gov/points/{latitude},{longitude}'

    response = requests.get(url)

    if response.status_code == 200:
        posts = response.json()
        return posts

    else:
        print('Error:', response.status_code)
        return None


def get_weather_forecasts(latitude, longitude):
    res = get_point(latitude, longitude)
    if not res:
        return None
    wfo = res['properties']['cwa']
    x = res['properties']['gridX']
    y = res['properties']['gridY']

    url = f'https://api.weather.gov/gridpoints/{wfo}/{x},{y}/forecast'

    response = requests.get(url)

    if response.status_code == 200:
        posts = response.json()
        return posts
    else:
        print('Error:', response.status_code)
        return None


def get_weather_info(city: str = None):
    latitude, longitude = get_coordinates(city)
    out = get_weather_forecasts(latitude, longitude)
    if not out:
        raise ValueError("Couldn't recognize your input.")
    current = out['properties']['periods'][0]
    today = current['startTime'][:10]
    forecasts = []
    count = 0

    for forecast in out['properties']['periods']:
        if 'Night' not in forecast['name'] and forecast['startTime'][:10] != today:
            forecast_date = datetime.fromisoformat(
                forecast['startTime']).strftime("%m/%d/%Y")
            forecast['name'] = f"({forecast_date}) {forecast['name']}"
            forecasts.append(forecast)
            count += 1
        if count == 5:
            break
    date = datetime.fromisoformat(current['startTime']).strftime("%m/%d/%Y")
    current['name'] = f"({date}) {current['name']}"

    return {'current': current, 'forecasts': forecasts}


def get_ip():
    response = requests.get('https://api64.ipify.org?format=json').json()
    return response["ip"]


def get_location():
    # ip_address = get_ip()
    # logger.info(request.headers)
    # logger.info(request)
    # logger.info(request.environ)
    # logger.info(requests.get('https://api64.ipify.org?format=json').json())
    # logger.info(f"request.remote_addr: {request.remote_addr}")
    # logger.info(f"request.remote_user: {request.remote_user}")

    if request.environ.get('HTTP_X_FORWARDED_FOR') is None:
        ip_address = request.environ['REMOTE_ADDR']
    else:
        ip_address = request.environ['HTTP_X_FORWARDED_FOR'] # if behind a proxy
    # logger.info(ip_address)
    
    # ip_address = request.headers.get('X-Forwarded-For', request.remote_addr)
    response = requests.get(f'https://ipapi.co/{ip_address}/json/').json()
    location_data = {
        "ip": ip_address,
        "city": response.get("city"),
        "region": response.get("region_code"),
        "country": response.get("country_name")
    }
    return location_data
