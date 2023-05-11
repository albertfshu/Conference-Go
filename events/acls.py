import requests
import json
from .keys import PEXELS_API_KEY, OPEN_WEATHER_API_KEY


def get_photo(city, state):
    url = "https://api.pexels.com/v1/search"
    headers = {"Authorization": PEXELS_API_KEY}
    params = {"query": city + " " + state}
    response = requests.get(url, params=params, headers=headers)

    content = response.content
    parsed_json = json.loads(content)
    picture = parsed_json["photos"][0]["src"]["original"]

    return {"picture_url": picture}


def get_lat_long(location):
    """Returns the latitude and longtitude for the specified location using the OpenWeatherMap API"""
    base_url = "https://api.openweathermap.org/geo/1.0/direct"
    params = {
        "q": f"{location.city},{location.state.abbreviation},USA",
        "appid": OPEN_WEATHER_API_KEY,
    }
    response = requests.get(base_url, params=params)
    parsed_json = json.loads(response.content)
    return {
        "latitude": parsed_json[0]["lat"],
        "longitude": parsed_json[0]["lon"],
    }


def get_weather_data(location):
    """Returns current weather data for the specific location using the OpenWeatherMap API"""

    lat_long = get_lat_long(location)
    base_url = "https://api.openweathermap.org/data/2.5/weather"
    params = {
        "lat": lat_long["latitude"],
        "lon": lat_long["longitude"],
        "appid": OPEN_WEATHER_API_KEY,
        "units": "imperial",
    }
    response = requests.get(base_url, params=params)
    parsed_json = json.loads(response.content)
    weather_data = {
        "temp": parsed_json["main"]["temp"],
        "description": parsed_json["weather"][0]["description"],
    }
    return weather_data

    # url = f"https://api.openweathermap.org/geo/1.0/direct?q={city},{state}&limit=1&appid=OPEN_WEATHER_API_KEY"
    # Create the URL for the geocoding API with the city and state
    # Make the request
    # Parse the JSON response
    # Get the latitude and longitude from the response
    # Create the URL for the current weather API with the latitude
    #   and longitude
    # Make the request
    # Parse the JSON response
    # Get the main temperature and the weather's description and put
    #   them in a dictionary
    # Return the dictionary
