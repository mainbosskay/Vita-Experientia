#!/usr/bin/python3
"""Module for comment model schema representing the database"""
from sqlalchemy import Column, ForeignKey, TIMESTAMP, String
from datetime import datetime

from . import Base


class Comment(Base):
    """Comment model class for posts or replys of comment"""
    __tablename__ = 'comments'
    id = Column(String(64), unique=True, nullable=False, primary_key=True)
    created_on = Column(TIMESTAMP(True), nullale=False,
                        default=datetime.utcnow())
    post_id = Column(String(64), ForeignKey('posts.id'), nullable=False)
    user_id = Column(String(64), ForeignKey('users.id'), nullable=False)
    comment_id = Column(String(64), nullable=True)
    content = Column(String(384), nullable=False)
