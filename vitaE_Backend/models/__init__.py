#!/usr/bin/python3
"""Module for utility function and base model"""
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import Column, TIMESTAMP, String
from sqlalchemy.sql import func, text
from datetime import datetime


Base = declarative_base()


class BaseModel:
    """Base model containing common attributes"""
    id = Column(String(64), unique=True, nullable=False, primary_key=True)
    created_on = Column(TIMESTAMP(True), nullable=False,
                        default=datetime.utcnow())
    updated_on = Column(TIMESTAMP(True), nullable=False,
                        default=datetime.utcnow(), onupdate=datetime.utcnow())

    def __init__(self, **kwargs):
        """Initializing base model with given attributes"""
        for key, val in kwargs.items():
            setattr(self, key, val)


def create_vectorts(*columns):
    """Create VectorTS column for full-text search"""
    vectorts_exp = columns[0]
    for col in columns[1:]:
        vectorts_exp = func.concat(vectorts_exp, ' ', col)
    return func.to_tsvector(text("'english'"), vectorts_exp)
