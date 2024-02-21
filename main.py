# -------------------------
import httpx, cachetools, datetime
from fastapi import FastAPI, HTTPException


# Создаем объект кэша с временем жизни 5 минут
cache = cachetools.TTLCache(maxsize=100, ttl=300)

app = FastAPI()
    
@app.get("/weather/{city}/?temperature={temperature}")
async def get_weather(city: str):
    try:
        # Проверяем, имеются ли закэшированные данные для данного запроса
        if city in cache:
            return cache[city] # Возвращаем закэшированные данные из кэша
    
        api_key = open('apikey', 'r').read()
        url = f'https://api.openweathermap.org/data/2.5/weather?q={city}&appid={api_key}&units=metric'

        async with httpx.AsyncClient() as client:
            response = await client.get(url)
            response.raise_for_status()

            data = response.json()

        weather = {
            'city': data['name'],
            'temperature': data['main']['temp'],
            # 'description': data['weather'][0]['description'],
            'feels': data['main']['feels_like'],
            'wind': data['wind']['speed'],
            'visibility': data['visibility'],
            'humidity': data['main']['humidity'],
            
        }

        # Кэшируем полученные данные с ключом - название города
        cache[city] = weather

        return weather
    except httpx.HTTPError:
        raise HTTPException(status_code=404, detail="City not found")
    except Exception:
        raise HTTPException(status_code=500, detail="Internal server error")


