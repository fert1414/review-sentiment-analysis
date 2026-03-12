from fastapi import Depends, FastAPI, Form, Request
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from sqlalchemy.orm import Session

from app.db import Base, engine, get_db
from app.models import Movie, Review
from app.tmdb import extract_imdb_id, fetch_all_reviews, find_movie_by_imdb_id, parse_tmdb_datetime
from app.status_checker import count_original_status

app = FastAPI(title='Review sentiment analysis')

Base.metadata.create_all(bind=engine)

templates = Jinja2Templates(directory='app/templates')

@app.get('/', response_class=HTMLResponse)
async def index(request: Request):
    return templates.TemplateResponse(
        'index.html',
        {
            'request': request
        }
    )

@app.post('/import', response_class=HTMLResponse)
async def import_reviews(
    request: Request,
    imdb_url: str = Form(...),
    db: Session = Depends(get_db)
):
    imdb_id = extract_imdb_id(imdb_url)
    tmdb_movie = await find_movie_by_imdb_id(imdb_id)

    tmdb_id = tmdb_movie['id']
    title = tmdb_movie.get('title') or 'Unknown title'

    movie = db.query(Movie).filter(Movie.imdb_id == imdb_id).first()

    if not movie:
        movie = Movie(
            imdb_id=imdb_id,
            tmdb_id=tmdb_id,
            title=title,
            imdb_url=imdb_url
        )
        db.add(movie)
        db.flush()
        db.refresh(movie)

    reviews_data = await fetch_all_reviews(tmdb_id)

    created_count = 0

    for item in reviews_data:
        tmdb_review_id = item.get('id')
        if not tmdb_review_id:
            continue

        existing_review = db.query(Review).filter(Review.tmdb_review_id == tmdb_review_id).first()

        if existing_review:
            continue

        author_details = item.get('author_details') or {}
        rating = author_details.get('rating')

        if not rating:
            continue
        
        review = Review(
            movie=movie,
            tmdb_review_id=tmdb_review_id,
            author=item.get('author'),
            author_username=author_details.get('username'),
            rating=int(rating) if isinstance(rating, (int, float)) else None,
            content=item.get('content') or '',
            review_url=item.get('url'),
            created_at=parse_tmdb_datetime(item.get('created_at')),
            updated_at=parse_tmdb_datetime(item.get('updated_at'))
        )

        db.add(review)
        created_count += 1

    db.commit()

    saved_reviews = db.query(Review).filter(Review.movie_id == movie.id).all()
    original_positive, original_negative = count_original_status(saved_reviews)

    return templates.TemplateResponse(
        'result.html',
        {
            'request': request,
            'movie': movie,
            'created_count': created_count,
            'total_reviews': len(saved_reviews),
            'original_positive': original_positive,
            'original_negative': original_negative
        }
    )
