#!/usr/bin/python3
"""Module for Post Model representing the database"""
from sqlalchemy import Column, String, ForeignKey, TEXT, Index
from sqlalchemy.dialects import postgresql
from sqlalchemy.orm import relationship
from sqlalchemy.sql import cast, func

from . import Base, BaseModel, create_vectorts


class Post(BaseModel, Base):
    """Post model for database representation"""
    __tablename__ = 'posts'
    user_id = Column(String(64), ForeignKey('users.id'), nullable=False)
    title = Column(String(256), nullable=False, default='', index=True)
    content = Column(TEXT, nullable=False, index=True)
    comments = relationship('Comment', cascade='all, delete, delete-orphan',
                            backref='post')
    likes = relationship('PostLike', cascade='all, delete, delete-orphan',
                         backref='post')
    __content_ts__ = create_vectorts(
        cast(func.coalesce(content, ''), postgresql.TEXT))
    __title_ts__ = create_vectorts(
        cast(func.coalesce(title, ''), postgresql.TEXT))
    __table_args__ = (
        Index('indx_vts_post_text', __content_ts__, postgresql_using='gin'),
        Index('indx_vts_post_title', __title_ts__, postgresql_using='gin')
    )
