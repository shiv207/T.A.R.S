import requests
import json

def get_weather(city):
    api_key = "43fd515d50f51222fb4cd9f608535c7d"  # Replace with your OpenWeatherMap API key
    base_url = f"http://api.openweathermap.org/data/2.5/weather?q={city}&appid={api_key}"
    
    try:
        response = requests.get(base_url)
        data = response.json()
        
        if response.status_code == 200:
            weather_description = data["weather"][0]["description"]
            temperature = data["main"]["temp"]
            return f"The weather in {city} is {weather_description}. Temperature: {temperature}°C"
        else:
            return "Unable to fetch weather information."
    except Exception as e:
        return f"Error: {str(e)}"