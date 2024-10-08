#!/usr/bin/python3
"""Module to add middlewares into FastAPI application"""
from fastapi import FastAPI
from starlette.middleware.gzip import GZipMiddleware
from starlette.middleware.cors import CORSMiddleware


def config_middlewares(app: FastAPI):
    """Setup and add all middleware to FastAPI app"""
    app.add_middleware(
        CORSMiddleware,
        allow_origins=['*'],
        allow_credentials=True,
        allow_methods=['*'],
        allow_headers=['*']
    )
    app.add_middleware(GZipMiddleware, minimum_size=1024)
