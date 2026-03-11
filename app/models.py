from sqlalchemy import Column, DateTime, ForeignKey, Integer, String, Text, UniqueConstraint
from sqlalchemy.orm import relationship

from app.db import Base

class Movie(Base):
    __tablename__ = 'movies'

    id = Column(Integer, primary_key=True, index=True)
    imdb_id = Column(String(20), unique=True, nullable=False, index=True)
    tmdb_id = Column(Integer, unique=True, nullable=False, index=True)
    title = Column(String(255), nullable=False)
    imdb_url = Column(String(500), nullable=False)

    reviews = relationship('Review', back_populates='movie', cascade='all, delete-orphan')

class Review(Base):
    __tablename__ = 'reviews'
    __table_args__ = (
        UniqueConstraint('tmdb_review_id', name='uq_reviews_tmdb_review_id'),
    )

    id = Column(Integer, primary_key=True, index=True)
    movie_id = Column(Integer, ForeignKey('movies.id'), nullable=False, index=True)

    tmdb_review_id = Column(String(100), nullable=False, index=True)
    author = Column(String(255), nullable=True)
    author_username = Column(String(255), nullable=True)
    rating = Column(Integer, nullable=True)
    content = Column(Text, nullable=False)
    review_url = Column(String(500), nullable=True)
    created_at = Column(DateTime(timezone=True), nullable=True)
    updated_at = Column(DateTime(timezone=True), nullable=True)

    movie = relationship('Movie', back_populates='reviews')