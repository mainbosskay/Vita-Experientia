#!/usr/bin/python3
"""Module for database connections and session management"""
import os
from sqlalchemy.orm import sessionmaker
from sqlalchemy import create_engine
from models import Base
from models.comment import Comment
from models.post import Post
from models.post_like import PostLike
from models.user import User
from models.user_following import UserFollowing


def get_engine():
    """Create and get database engine"""
    db_url = os.getenv('DATABASE_URL')
    engine = create_engine(db_url, pool_pre_ping=True)
    return engine


def init_database():
    """Delete and creates database tables"""
    engine = get_engine()
    Base.metadata.drop_all(engine)
    Base.metadata.create_all(engine)


def get_session():
    """Get new SQLAlchemy session"""
    engine = get_engine()
    SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
    Base.metadata.create_all(engine)
    session = SessionLocal()
    return session
