#!/usr/bin/python3
"""Module for configuration and execution of API server"""
import os
import uvicorn
from fastapi import FastAPI
from fastapi.responses import JSONResponse
from fastapi.exceptions import RequestValidationError
from starlette.exceptions import HTTPException as StarletteHTTPException


from .middlewares import config_middlewares
from .endpoint import config_endpoints


app = FastAPI()
config_middlewares(app)
config_endpoints(app)


async def handler_exceptions(request, exc):
    """Manages exceptions and return a JSON response"""
    error_message = f'[{exc.__class__.__name__}]: Request failed.'
    api_response = {
        'success': False,
        'message': str(exc) if exc else error_message
    }
    return JSONResponse(api_response)


app.add_exception_handler(StarletteHTTPException, handler_exceptions)
app.add_exception_handler(RequestValidationError, handler_exceptions)
app.add_exception_handler(Exception, handler_exceptions)


if __name__ == '__main__':
    uvicorn.run(
        'api.v1.server:app',
        host=os.getenv('HOST', '0.0.0.0'),
        port=5000,
        log_level='info'
    )
