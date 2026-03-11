import os
import re
from datetime import datetime
from urllib.parse import urlparse

import httpx
from dotenv import load_dotenv
from fastapi import HTTPException

load_dotenv()

TMDB_API_BASE = 'https://api.themoviedb.org/3'
TMDB_ACCESS_TOKEN = os.getenv('TMDB_ACCESS_TOKEN')

def get_headers() -> dict[str, str]:
    if not TMDB_ACCESS_TOKEN:
        raise HTTPException(status_code=500, detail='Не задан TMDB_ACCESS_TOKEN')

    return {
        'accept': 'application/json',
        'Authorization': f'Bearer {TMDB_ACCESS_TOKEN}'
    }

def extract_imdb_id(imdb_url: str) -> str:
    parsed = urlparse(imdb_url)

    if 'imdb.com' not in parsed.netloc:
        raise HTTPException(status_code=400, detail='Нужна ссылка на imdb.com')

    match = re.search(r'/title/(tt\d+)', parsed.path)
    if not match:
        raise HTTPException(status_code=400, detail='Не удалось извлечь IMDb ID из ссылки')
    
    return match.group(1)

async def find_movie_by_imdb_id(imdb_id: str) -> dict:
    url = f'{TMDB_API_BASE}/find/{imdb_id}'
    params = {'external_source': 'imdb_id'}

    async with httpx.AsyncClient(timeout=30.0) as client:
        response = await client.get(url, params=params, headers=get_headers())

    if response.status_code != 200:
        raise HTTPException(status_code=502, detail=f'TMDB find error: {response.text}')
    
    data = response.json()
    movie_results = data.get('movie_results', [])

    if not movie_results:
        raise HTTPException(status_code=404, detail='Фильм не найден в TMDB')

    return movie_results[0]

def parse_tmdb_datetime(value: str | None):
    if not value:
        return None

    try:
        return datetime.fromisoformat(value.replace('Z', '+00:00'))
    except ValueError:
        return None

async def fetch_all_reviews(tmdb_movie_id: int) -> list[dict]:
    page = 1
    reviews = []

    async with httpx.AsyncClient(timeout=30.0) as client:
        while True:
            url = f'{TMDB_API_BASE}/movie/{tmdb_movie_id}/reviews'
            params = {
                'page': page,
                'language': 'en-US'
            }

            response = await client.get(url, params=params, headers=get_headers())
            if response.status_code != 200:
                raise HTTPException(status_code=502, detail=f'TMDB find error: {response.text}')

            data = response.json()
            results = data.get('results', [])
            total_pages = data.get('total_pages', 1)

            reviews.extend(results)

            if page >= total_pages:
                break

            page += 1
    
    return reviews