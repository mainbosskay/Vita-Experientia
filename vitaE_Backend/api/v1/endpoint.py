#!/usr/bin/python3
"""Module for all API endpoints registration with application"""
from fastapi import FastAPI

from .endpoints import (
    home_endpoint, authentication, user, connection, post, comment, search
)


def config_endpoints(app: FastAPI):
    """Set up and add all endpoints to the FastAPI app"""
    app.include_router(home_endpoint)
    app.include_router(authentication.endpoint)
    app.include_router(comment.endpoint)
    app.include_router(connection.endpoint)
    app.include_router(post.endpoint)
    app.include_router(search.endpoint)
    app.include_router(user.endpoint)
