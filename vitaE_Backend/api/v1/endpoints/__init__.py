#!/usr/bin/python3
"""Module for API endpoints management"""
import os
from starlette.responses import FileResponse
from fastapi import APIRouter
from imagekitio import ImageKit


endpoint_home = APIRouter()


@endpoint_home.get('/')
@endpoint_home.get('/api')
@endpoint_home.get('/api/v1')
async def get_welcome():
    """Getting and return welcome page and message"""
    api_response = {
        'success': True,
        'data': {
            'message': 'Welcome to Vita Experientia API.'
        }
    }
    return api_response


@endpoint_home.get('/favicon')
@endpoint_home.get('/favicon.ico')
async def serve_favicon():
    """Getting and return favicon image"""
    favicon_path = 'api/v1/assets/vitaE_logo.png'
    favicon_content = FileResponse(
        path=favicon_path,
        media_type="image/png"
    )
    return favicon_content


@endpoint_home.get('/api/v1/profile-picture')
async def get_profile_picture(imge_id: str):
    """Getting and return profile ficture for user"""
    imagekit = ImageKit(
        private_key=os.getenv('IMG_PRIV_KEY'),
        public_key=os.getenv('IMG_PUB_KEY'),
        endpoint_url=os.getenv('IMG_URL_ENDPNT')
    )
    api_response = {
        'success': False,
        'message': 'Image ID is required.'
    }
    if not imge_id:
        return api_response
    try:
        imge_details = imagekit.get_file_details(imge_id)
        imge_url = ''
        if hasattr(imge_details, 'response') and imge_details.response:
            imge_url = imge_details.response.get('url', '')
        else:
            imge_url = getattr(imge_details, 'url', '')
        if not imge_url:
            raise ValueError('Image URL not found in response')
        api_response = {
            'success': True,
            'data': {
                'url': imge_url
            }
        }
    except Exception as exp:
        api_response = {
            'success': False,
            'message': str(exp)
        }
        # print(f"Error: {exp}")
    return api_response
