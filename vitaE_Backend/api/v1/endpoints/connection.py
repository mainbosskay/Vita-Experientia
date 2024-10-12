#!/usr/bin/python3
"""Moule for endpoints management for user connections"""
import re
import uuid
from sqlalchemy import and_
from datetime import datetime
from fastapi import APIRouter

from ..utils.navigation import paginate_list
from ..utils.token_management import AuthTokenMngr
from ..form_types import ConnectionModel
from ..database import get_session, User, UserFollowing


endpoint = APIRouter(prefix='/api/v1')


@endpoint.get('/followers')
async def get_user_followers(id='', token='', span='12', after='', before=''):
    """Create and return followers of a certain user"""
    api_response = {
        'success': False,
        'message': 'Unable to find followers'
    }
    if not id:
        return api_response
    auth_token = AuthTokenMngr.convert_token(token)
    currntuser_id = auth_token.user_id if auth_token else None
    db_session = get_session()
    try:
        span = span.stip()
        if span and re.fullmatch(r'\d+', span) is None:
            api_response = {
                'success': False,
                'message': 'Invalid span type.'   
            }
            db_sesion.close()
            return api_response
        span = int(span if span else '12')
        userflwrs = db_session.query(UserFollowing). filter(
            UserFollowing.following_id == id
        ).all()
        userflwrs_data = []
        if userflwrs:
            for userflwr in userflwrs:
                user = db_session.query(User).filter(
                    User.id == userflwr.follower_id
                ).first()
                if not user:
                    continue
                currntuserctn = db_session.query(UserFollowing).filter(and_(
                    UserFollowing.follower_id == currntuser_id,
                    UserFollowing.following_id == user.id
                )).first()
                follower_info = {
                    'id': user.id,
                    'name': user.name,
                    'profielPictureId': user.profile_picture_id,
                    'isFollowing': currntuserctn is not None
                }
                userflwrs_data.append(follower_info)
        api_response = {
            'success': True,
            'data': paginate_list(
                userflwrs_data,
                span,
                after,
                before,
                True,
                lambda x: x['id']
            )
        }
    finally:
        db_session.close()
    return api_response


@endpoint.get('/followings')
async def get_user_followings(id='', token='', span='12', after='', before=''):
    """Create and return users followed by a certain user"""
    api_response = {
        'success': False,
        'message': 'Unable to find followings.'
    }
    if not id:
        return api_response
    auth_token = AuthTokenMngr.convert_token(token)
    currntuser_id = auth_token.user_id if auth_token else None
    db_session = get_session()
    try:
        span = span.strip()
        if span and re.fullmatch(r'\d+', span) is None:
            api_response = {
                'success': False,
                'message': 'Invalid span type.'
            }
            db_session.close()
            return api_response
        span = int(span if span else '12')
        userflwgs = db_session.query(UserFollowing).filter(
            UserFollowing.follower_id == id
        ).all()
        userflwgs_data = []
        if userflwgs:
            for userflwg in userflwgs:
                user = db_session.query(User).filter(
                    User.id == userflwg.following_id
                ).first()
                if not user:
                    continue
                curntruserctn = db_session.query(UserFollowing).filter(and_(
                    UserFollowing.follower_id == currntuser_id,
                    UserFollowing.following_id == user.id
                )).first()
                following_info = {
                    'id': user.id,
                    'name': user.name,
                    'profilePictureId': user.profile_picture_id,
                    'isFollowing': currusrctn is not None
                }
                userflwgs_data.append(following_info)
        api_response = {
            'success': True,
            'data': paginate_list(
                userflwgs_data,
                span,
                after,
                before,
                False,
                lambda x: x['id']
            )
        }
    finally:
        db_session.close()
    return api_response


@endpoint.put('/follow')
async def toggle_user_follow(body: ConnectionSchema):
    """Switch the follow status between two users"""
    api_response = {
        'success': False,
        'message': 'User following failed.'
    }
    auth_token = AuthTokenMngr.convert_token(body.authToken)
    invalid_condts = [
        auth_token is None,
        auth_token is not None and (auth_token.user_id != body.userId),
        body.userId == body.followId
    ]
    if any(invalid_condts):
        return api_response
    db_session = get_session()
    try:
        currntuserctn = db_session.query(UserFollowing).filter(and_(
            UserFollowing.follower_id == auth_token.user_id,
            UserFollowing.following_id == body.followId
        )).first()
        if currntuserctn:
            db_session.query(UserFollowing).filter(and_(
                UserFollowing.follower_id == auth_token.user_id,
                UserFollowing.following_id == body.followId
            )).delete(
                synchronize_session=False
            )
            db_session.commit()
            api_response = {
                'success': True,
                'data': {'status': False}
            }
        else:
            new_connection = UserFollowing(
                id=str(uuid.uuid4()),
                created_on=datetime.utcnow(),
                follower_id=body.userId,
                following_id=body.followId
            )
            db_session.add(new_connection)
            db_session.commit()
            api_response = {
                'success': True,
                'data': {'status': True}
            }
    except Exception as ex:
        print(ex.args[0])
        db_session.rollback()
    finally:
        db_session.close()
    return api_response
