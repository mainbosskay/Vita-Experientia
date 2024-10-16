#!/usr/bin/python3
"""Module for handling user related endpoints"""
import os
import email_validator
from datetime import datetime
from fastapi import APIRouter
from sqlalchemy import and_, or_
from imagekitio import ImageKit

from ..form_types import UserUpdateModel, UserDeleteModel
from ..utils.token_management import AuthTokenMngr
from ..database import (
    get_session,
    User,
    UserFollowing,
    Post,
    PostLike,
    Comment
)


endpoint = APIRouter(prefix='/api/v1')


@endpoint.get('/user')
async def get_user(id: str, token=''):
    """Create and return info on a certain user"""
    api_response = {
        'success': False,
        'message': 'User not found.'
    }
    auth_token = AuthTokenMngr.convert_token(token)
    if id is None:
        return api_response
    user_id = auth_token.user_id if auth_token is not None else ''
    db_session = get_session()
    try:
        user = db_session.query(User).filter(User.id == id).first()
        if user:
            followers = db_session.query(UserFollowing).filter(
                UserFollowing.following_id == user.id
            ).all()
            followings = db_session.query(UserFollowing).filter(
                UserFollowing.follower_id == user.id
            ).all()
            posts = db_session.query(Post).filter(
                Post.user_id == user.id
            ).all()
            likes = db_session.query(PostLike).filter(
                PostLike.user_id == user.id
            ).all()
            comments = db_session.query(Comment).filter(
                Comment.user_id == user.id
            ).all()
            currntuser_ctn = db_session.query(UserFollowing).filter(and_(
                UserFollowing.follower_id == user.id,
                UserFollowing.following_id == user.id
            )).first()
            flwrs_count = len(followers) if followers else 0
            flwngs_count = len(followings) if followings else 0
            posts_count = len(posts) if posts else 0
            like_count = len(likes) if likes else 0
            comment_count = len(comments) if comments else 0
            api_response = {
                'success': True,
                'data': {
                    'id': user.id,
                    'joined': user.created_on.isoformat(),
                    'name': user.name,
                    'email': user.email if user.id == user_id else '',
                    'bio': user.bio,
                    'profilePictureId': user.profile_picture_id,
                    'followersCount': flwrs_count,
                    'followingsCount': flwngs_count,
                    'postsCount': posts_count,
                    'likesCount': like_count,
                    'commentsCount': comment_count,
                    'isFollowing': currntuser_ctn is not None
                }
            }
    finally:
        db_session.close()
    return api_response


@endpoint.put('/user')
async def update_user_info(body: UserUpdateModel):
    """Modify the user's profile info"""
    api_response = {
        'success': False,
        'message': 'Update user profile failed.'
    }
    auth_token = AuthTokenMngr.convert_token(body.authToken)
    if auth_token is None or (auth_token.user_id != body.userId):
        api_response['message'] = 'Invalid authentication token.'
        return api_response
    if len(body.name) > 64:
        api_response['message'] = 'User name is too long.'
        return api_response
    elif len(body.bio) > 384:
        api_response['message'] = 'Bio is too long.'
    db_session = get_session()
    imagekit = ImageKit(
        private_key=os.getenv('IMG_PRIV_KEY'),
        public_key=os.getenv('IMG_PUB_KEY'),
        url_endpoint=os.getenv('IMG_URL_ENDPNT')
    )
    try:
        email_validator.validate_email(body.email)
        profile_pic_file_id = body.profilePictureId.strip()
        if body.removeProfilePicture:
            if profile_pic_file_id:
                imagekit.delete_file(profile_pic_file_id)
                profile_pic_file_id = ''
        if body.profilePicture and not body.removeProfilePicture:
            if profile_pic_file_id:
                imagekit.delete_file(profile_pic_file_id)
            user = db_session.query(User).filter(
                User.id == body.userId
            ).first()
            if user.profile_picture_id:
                imagekit.delete_file(user.profile_picture_id)
            upload_res = imagekit.upload_file(
                file=body.profilePicture,
                file_name=f"{body.userId.replace('-', '')}",
                options={
                    'folder': 'vitaexperientia/profile_pictures',
                    'is_private_file': False
                }
            )
            if upload_res['response']:
                profile_pic_file_id = upload_res['response']['fileId']
                print(profile_pic_file_id)
            if upload_res['error']:
                raise ValueError(upload_res['error']['message'])
        db_session.query(User).filter(User.id == body.userId).update(
            {
                User.updated_on: datetime.utcnow(),
                User.name: body.name,
                User.profile_picture_id: profile_pic_file_id,
                User.email: body.email,
                User.bio: body.bio
            },
            synchronize_session=False
        )
        db_session.commit()
        new_auth_token = AuthTokenMngr(
            user_id=body.userId,
            email=body.email,
            secure_text=auth_token.secure_text
        )
        api_response = {
            'success': True,
            'data': {
                'authToken': AuthTokenMngr.encode_token(new_auth_token),
                'profilePictureId': profile_pic_file_id
            }
        }
    except email_validator.EmailNotValidError as ex:
        api_response['message'] = 'Invalid email.'
    except Exception as ex:
        print(ex.args[0])
    finally:
        db_session.rollback()
        db_session.close()
    return api_response


@endpoint.delete('/user')
async def remove_user(body: UserDeleteModel):
    """Deleting user data and account permanently"""
    api_response = {
        'success': False,
        'message': 'Failed to delete user data.'
    }
    auth_token = AuthTokenMngr.convert_token(body.authToken)
    if auth_token is None or auth_token.user_id != body.userId:
        api_response['message'] = 'Invalid authentication token.'
        return api_response
    db_session = get_session()
    try:
        db_session.query(UserFollowing).filter(or_(
            UserFollowing.follower_id == body.userId,
            UserFollowing.following_id == body.userId
        )).delete(
            synchronize_session=False
        )
        db_session.query(PostLike).filter(
            PostLike.user_id == body.userId
        ).delete(
            synchronize_session=False
        )
        comments = db_session.query(Comment).filter(and_(
            Comment.user_id == body.userId,
            Comment.comment_id == None
        )).all()
        comment_ids = map(lambda x: x.id, comments)
        db_session.query(Comment).filter(or_(
            Comment.comment_id.in_(comment_ids),
            Comment.user_id == body.userId
        )).delete(
            synchronize_session=False
        )
        db_session.query(Post).filter(
            Post.user_id == body.userId
        ).delete(
            synchronize_session=False
        )
        db_session.query(User).filter(
            User.id == body.userId
        ).delete(
            synchronize_session=False
        )
        db_session.commit()
        api_response = {
            'success': True,
            'data': {}
        }
    finally:
        db_session.close()
    return api_response
