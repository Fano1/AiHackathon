import asyncio
import aiohttp
import urllib.parse
from datetime import datetime
from api import GEMINI_KEY, KEY
from google import genai
from google.genai import types
from concurrent.futures import ThreadPoolExecutor

client = genai.Client(api_key=GEMINI_KEY)
headers = {
    'User-Agent': 'MyPythonClient/1.0'  # Don’t skip this or Nominatim slaps you
}

def get_season():
    month = datetime.now().month
    return {
        (12, 1, 2): "Winter",
        (3, 4, 5): "Spring",
        (6, 7, 8): "Summer",
        (9, 10, 11): "Autumn"
    }[tuple(filter(lambda m: month in m, [(12, 1, 2), (3, 4, 5), (6, 7, 8), (9, 10, 11)]))[0]]

async def get_lat_lon(session, address):
    url = f'https://nominatim.openstreetmap.org/search?q={urllib.parse.quote(address)}&format=json'
    async with session.get(url, headers=headers) as resp:
        data = await resp.json()
        return float(data[0]['lat']), float(data[0]['lon'])

async def get_soil_ph(session, lat, lon):
    url = f"https://rest.isric.org/soilgrids/v2.0/properties/query?lon={lon}&lat={lat}&property=phh2o&value=mean"
    async with session.get(url) as resp:
        data = await resp.json()
        return data['properties']['layers'][0]['depths'][0]['values']['mean']

async def get_weather(session, lat, lon):
    url = f"http://api.openweathermap.org/data/2.5/weather?lat={lat}&lon={lon}&appid={KEY}&units=metric"
    async with session.get(url) as resp:
        data = await resp.json()
        return {
            "temp": data["main"]["temp"],
            "humidity": data["main"]["humidity"],
            "weather": data["weather"][0]["main"]
        }

def generateDefaultText(content):
    response = client.models.generate_content(
        model = "gemini-2.0-flash",

        contents=[content],
        config=types.GenerateContentConfig(
            max_output_tokens=800,
            temperature=0.1 #randomness of the model 
            #holy shit the prompt model fucks everything up, dont touch the topk and bottomk
        )
    )
    return response.text.strip()

executor = ThreadPoolExecutor()

async def get_gemini_advice(weather, soil_ph, season):
    loop = asyncio.get_event_loop()
    prompt = f"""
    Based on the following environmental conditions:
    
    - Weather: {weather['weather']}, Temperature: {weather['temp']}°C, Humidity: {weather['humidity']}%
    - Soil pH: {soil_ph}
    - Current season: {season}

    Suggest the most suitable crops to plant and give brief farming advice for a small-scale farmer.
    Keep it practical and easy to understand.
    """
    return await loop.run_in_executor(executor, generateDefaultText, prompt)


async def analyze_location(address):
    async with aiohttp.ClientSession() as session:
        try:
            lat, lon = await get_lat_lon(session, address)
            season = get_season()

            # Concurrent API calls
            soil_task = asyncio.create_task(get_soil_ph(session, lat, lon))
            weather_task = asyncio.create_task(get_weather(session, lat, lon))

            soil_ph = await soil_task
            weather = await weather_task

            advice = await get_gemini_advice(weather, soil_ph, season)

            return (
                f"Location: {lat}, {lon}\n"
                f"Season: {season}\n"
                f"Soil pH: {soil_ph}\n"
                f"Weather: {weather['weather']}, Temp: {weather['temp']}°C, Humidity: {weather['humidity']}%\n\n"
                f"Gemini's Agricultural Advice:\n{advice}"
            )

        except Exception as e:
            return f" Error: {e}"


