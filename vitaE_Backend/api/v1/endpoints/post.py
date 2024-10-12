#!/usr/bin/python3
"""Module for handling post-related API endpoints"""
import re
import uuid
import json
from sqlalchemy import and_
from datetime import datetime
from fastapi import APIRouter

from ..utils.token_management import AuthTokenMngr
from ..database import (
    get_session, User, Comment, Post, PostLike, UserFollowing)
from ..form_types import (
    PostAddModel, PostUpdateModel, PostLikeModel, PostDeleteModel)
from ..utils.navigation import paginate_list


endpoint = APIRouter(prefix='/api/v1')


@endpoint.get('/post')
async def get_post(id: str, token: str):
    """Create and return infomation about a certain post"""
    api_response = {
        'success': False,
        'message': 'Post not found.'
    }
    auth_token = AuthTokenMngr.convert_token(token)
    user_id = auth_token.user_id if auth_token is not None else None
    db_session = get_session()
    try:
        post = db_session.query(Post).filter(Post.id == id).first()
        if post:
            user = db_session.query(User).filter(
                User.id == post.user_id
            ).first()
            if not user:
                return api_response
            comments = db_session.query(Comment).filter(and_(
                Comment.post_id == id,
                Comment.comment_id == None
            )).all()
            comment_count = len(comments) if comments else 0
            likes = db_session.query(PostLike).filter(
                PostLike.post_id == id
            ).all()
            like_count = len(likes) if likes else 0
            is_liked_by_user = False
            if user_id:
                post_dits = db_session.query(PostLike).filter(and_(
                    PostLike.post_id == id,
                    PostLike.user_id == user_id
                )).first()
                if post_dits:
                    is_liked_by_user = True
            api_response = {
                'success': True,
                'data': {
                    'id': post.id,
                    'user': {
                        'id': user.id,
                        'name': user.name,
                        'profilePictureId': user.profile_picture_id
                    },
                    'title': post.title,
                    'publishedOn': post.created_on.isoformat(),
                    'quotes': json.JSONDecoder().decode(post.content),
                    'commentsCount': comment_count,
                    'likesCount': like_count,
                    'isLiked': is_liked_by_user
                }
            }
    finally:
        db_session.close()
    return api_response


@endpoint.post('/post')
async def create_post(body: PostAddModel):
    """Get a new post entry"""
    api_response = {
        'success': False,
        'message': 'Failed creation of post.'
    }
    auth_token = AuthTokenMngr.convert_token(body.authToken)
    if auth_token is None or auth_token.user_id != body.userId:
        api_response['message'] = 'Invalid authentication token.'
        return api_response
    if len(body.title) > 256:
        api_response['message'] = 'Title exceeds length limit.'
        return api_response
    if len(body.stories) < 1:
        api_response['message'] = 'Stories are too short.'
        return api_response
    if not all(list(map(lambda x: len(x.strip()) > 1, body.stories))):
        api_response['message'] = 'Stories are too short.'
        return api_response
    db_session = get_session()
    try:
        gen_id = str(uuid.uuid4())
        currntdt = datetime.utcnow()
        stories_txt = json.JSONEncoder().encode(body.stories)
        post = Post(
            id=gen_id,
            created_on=currntdt,
            updated_on=currntdt,
            user_id=body.userId,
            title=body.title,
            content=stories_txt
        )
        db_session.add(post)
        db_session.commit()
        api_response = {
            'success': True,
            'data': {
                'id': gen_id,
                'createdOn': currntdt.isoformat(),
                'repliesCount': 0,
                'likesCount': 0
            }
        }
    except Exception as ex:
        print(ex.args[0])
        db_session.rollback()
    finally:
        db_session.close()
    return api_response


@endpoint.put('/post')
async def modify_post(body: PostUpdateModel):
    """Modify the content and an existing post"""
    api_response = {
        'success': False,
        'message': 'Failed to update post.'
    }
    auth_token = AuthTokenMngr.convert_token(body.authToken)
    if auth_token is None or auth_token.user_id != body.userId:
        api_response['message'] = 'Invalid authentication token.'
        return api_response
    if len(body.title) > 256:
        api_response['message'] = 'Title exceeds length limit.'
        return api_response
    if len(body.stories) < 1:
        api_response['message'] = 'Stories are too short.'
        return api_response
    if not all(list(map(lambda x: len(x.strip()) > 1, body.stories))):
        api_response['message'] = 'Stories are too short.'
        return api_response
    db_session = get_session()
    try:
        currntdt = datetime.utcnow()
        stories_txt = json.JSONEncoder().encode(body.quotes)
        db_session.query(Post).filter(Post.id == body.postId).update(
            {
                Post.title: body.title,
                Post.updated_on: currntdt,
                Post.content: stories_txt
            },
            synchronize_session=False
        )
        db_session.commit()
        api_response = {
            'success': True,
            'data': {}
        }
    except Exception as ex:
        print(ex.args[0])
        db_session.rollback()
    finally:
        db_session.close()
    return api_response


@endpoint.delete('/post')
async def delete_post(body: PostDeleteModel):
    """Remove a post permanently"""
    api_response = {
        'success': False,
        'message': 'Failed to delete post.'
    }
    auth_token = AuthTokenMngr.convert_token(body.authToken)
    if auth_token is None or auth_token.user_id != body.userId:
        api_response['message'] = 'Invalid authentication token.'
        return api_response
    db_session = get_session()
    try:
        post = db_session.query(Post).filter(and_(
            Post.id == body.postId,
            Post.user_id == body.userId
        )).first()
        if post:
            db_session.query(PostLike).filter(
                PostLike.post_id == body.postId
            ).delete(
                synchronize_session=False
            )
            db_session.query(Comment).filter(
                Comment.post_id == body.postId
            ).delete(
                synchronize_session=False
            )
            db_session.query(Post).filter(and_(
                Post.id == body.postId,
                Post.user_id == body.userId
            )).delete(
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


@endpoint.put('/like-post')
async def like_post(body: PostLikeModel):
    """Switch like status on a post"""
    api_response = {
        'success': False,
        'message': 'Failed to like post.'
    }
    auth_token = AuthTokenMngr.convert_token(body.authToken)
    if auth_token is None or auth_token.user_id != body.userId:
        api_response['message'] = 'Invalid authentication token.'
        return api_response
    db_session = get_session()
    try:
        prevlike = db_session.query(PostLike).filter(and_(
            PostLike.user_id == auth_token.user_id,
            PostLike.post_id == body.postId
        )).first()
        if prevlike:
            db_session.query(PostLike).filter(and_(
                PostLike.user_id == auth_token.user_id,
                PostLike.post_id == body.postId
            )).delete(
                synchronize_session=False
            )
            db_session.commit()
            api_response = {
                'success': True,
                'data': {'status': False}
            }
        else:
            new_like = PostLike(
                id=str(uuid.uuid4()),
                created_on=datetime.utcnow(),
                user_id=body.userId,
                post_id=body.postId
            )
            db_session.add(new_like)
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


@endpoint.get('/posts-user-made')
async def get_users_posts(userId, token='', span='', after='', before=''):
    """Create and return posts made by the present user"""
    api_response = {
        'success': False,
        'message': 'Failed to find posts by the user.'
    }
    if not userId:
        return api_response
    auth_token = AuthTokenMngr.convert_token(token)
    currntuser_id = auth_token.user_id if auth_token is not None else None
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
        posts_made = db_session.query(Post).filter(
            Post.user_id == userId
        ).all()
        post_data = []
        if posts_made:
            user = db_session.query(User).filter(
                User.id == userId
            ).first()
            if not user:
                return api_response
            for post in posts_made:
                comments = db_session.query(Comment).filter(and_(
                    Comment.post_id == post.id,
                    Comment.comment_id == None
                )).all()
                comment_count = len(comments) if comments else 0
                likes = db_session.query(PostLike).filter(
                    PostLike.post_id == post.id
                ).all()
                like_count = len(likes) if likes else 0
                is_liked_by_user = False
                if currntuser_id:
                    post_dits = db_session.query(PostLike).filter(and_(
                        PostLike.post_id == post.id,
                        PostLike.user_id == currntuser_id
                    )).first()
                    if post_dits:
                        is_liked_by_user = True
                post_info = {
                    'id': post.id,
                    'user': {
                        'id': user.id,
                        'name': user.name,
                        'profilePictureId': user.profile_picture_id
                    },
                    'title': post.title,
                    'publishedOn': post.created_on.isoformat(),
                    'qoutes': json.JSONDecoder().decode(post.content),
                    'commentsCount': comment_count,
                    'likesCount': like_count,
                    'isLiked': is_liked_by_user
                }
                post_data.append(post_info)
        post_data.sort(
            key=lambda x: datetime.fromisoformat(x['publishedOn']),
            reverse=True
        )
        api_response = {
            'success': True,
            'data': paginate_list(
                post_data,
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


@endpoint.get('/posts-user-likes')
async def get_liked_posts(userId, token='', span='', after='', before=''):
    """Create and return liked post by a user"""
    api_response = {
        'success': False,
        'message': 'No posts liked by the user.'
    }
    if not userId:
        return api_response
    auth_token = AuthTokenMngr.convert_token(token)
    user_id = auth_token.user_id if auth_token is not None else None
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
        likes = db_session.query(PostLike).filter(
            PostLike.user_id == userId
        ).all()
        liked_posts = []
        for post_like in likes:
            post = db_session.query(Post).filter(
                Post.id == post_like.post_id
            ).first()
            user = db_session.query(User).filter(
                User.id == post.user_id
            ).first()
            comments = db_session.query(Comment).filter(and_(
                Comment.post_id == post.id,
                Comment.comment_id == None
            )).all()
            comment_count = len(comments) if comments else 0
            likes = db_session.query(PostLike).filter(
                PostLike.post_id == post.id
            ).all()
            like_count = len(likes) if likes else 0
            is_liked_by_user = False
            if user_id != userId:
                post_dits = db_session.query(PostLike).filter(and_(
                    PostLike.post_id == post.id,
                    PostLike.user_id == user_id
                )).first()
                if post_dits:
                    is_liked_by_user = True
            else:
                is_liked_by_user = True
            likes_info = {
                'id': post.id,
                'user': {
                    'id': user.id,
                    'name': user.name,
                    'profilePictureId': user.profile_picture_id
                },
                'title': post.title,
                'publishedOn': post.created_on.isoformat(),
                'quotes': json.JSONDecoder().decode(post.content),
                'commentsCount': comment_count,
                'likesCount': like_count,
                'isLiked': is_liked_by_user
            }
            liked_posts.append(likes_info)
        liked_posts.sort(
            key=lambda x: datetime.fromisoformat(x['publishedOn'])
        )
        api_response = {
            'success': True,
            'data': paginate_list(
                liked_posts,
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


@endpoint.get('/posts-feed')
async def get_feed_posts(token, span='', after='', before=''):
    """Create and return user's feed post"""
    api_response = {
        'success': False,
        'message': 'Failed to find post for the feed.'
    }
    auth_token = AuthTokenMngr.convert_token(token)
    if auth_token is None:
        api_response['message'] = 'Invalid authentication token.'
        return api_response
    user_id = auth_token.user_id
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
            UserFollowing.follower_id == user_id
        ).all()
        max_size = 2**32 - 1
        flwngs_count = len(userflwgs) + 1 if userflwgs else 1
        posts_per_flwngs = max_size // flwngs_count
        posts_users_ids = [user_id]
        if userflwgs:
            posts_users_ids.extend(list(
                map(lambda x: x.following_id, userflwgs)))
        posts_data = []
        for id in posts_users_ids:
            posts = db_session.query(Post).filter(
                Post.user_id == id
            ).limit(posts_per_flwngs).all()
            user = db_session.query(User).filter(
                User.id == id
            ).first()
            for post in posts:
                comments = db_session.query(Comment).filter(and_(
                    Comment.post_id == post.id,
                    Comment.comment_id == None
                )).all()
                comment_count = len(comments) if comments else 0
                likes = db_session.query(PostLike).filter(
                    PostLike.post_id == post.id
                ).all()
                like_count = len(likes) if likes else 0
                is_liked_by_user = False
                if user_id:
                    post_dits = db_session.query(PostLike).filter(and_(
                        PostLike.post_id == post.id,
                        PostLike.user_id == user_id
                    )).first()
                    if post_dits:
                        is_liked_by_user = True
                post_info = {
                    'id': post.id,
                    'user': {
                        'id': user.id,
                        'name': user.name,
                        'profilePictureId': user.profile_picture_id
                    },
                    'title': post.title,
                    'publishedOn': post.created_on.isoformat(),
                    'quotes': json.JSONDecoder().decode(post.content),
                    'commentsCount': comment_count,
                    'likesCount': like_count,
                    'isLiked': is_liked_by_user
                }
                posts_data.append(post_info)
        posts_data.sort(
            key=lambda x: datetime.fromisoformat(x['publishedOn']),
            reverse=True
        )
        api_response = {
            'success': True,
            'data': paginate_list(
                posts_data,
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


@endpoint.get('/posts-explore')
async def get_exploratory_posts(token, span='', after='', before=''):
    """Create and return posts for the explore section"""
    api_response = {
        'success': False,
        'message': 'Failed to find posts for the explore section.'
    }
    auth_token = AuthTokenMngr.convert_token(token)
    if auth_token is None:
        api_response['message'] = 'Invalid authentication token.'
        return api_response
    user_id = auth_token.user_id if auth_token is not None else None
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
            UserFollowing.follower_id == user_id
        ).all()
        max_posts_count = 48
        post_users_ids = [user_id]
        if userflwgs:
            post_users_ids.extend(
                list(map(lambda x: x.following_id, userflwgs))
            )
        explore_posts = []
        posts = db_session.query(Post).filter(
            Post.user_id.notin_(post_users_ids)
        ).limit(max_posts_count).all()
        for post in posts:
            user = db_session.query(User).filter(
                User.id == post.user_id
            ).first()
            comments = db_session.query(Comment).filter(and_(
                Comment.post_id == post.id,
                Comment.comment_id == None
            )).all()
            comment_count = len(comments) if comments else 0
            likes = db_session.query(PostLike).filter(
                PostLike.post_id == post.id
            ).all()
            like_count = len(likes) if likes else 0
            is_liked_by_user = False
            if user_id:
                post_dits = db_session.query(PostLike).filter(and_(
                    PostLike.post_id == post.id,
                    PostLike.user_id == user_id
                )).first()
                if post_dits:
                    is_liked_by_user = True
            post_info = {
                'id': post.id,
                'user': {
                    'id': user.id,
                    'name': user.name,
                    'profilePictureId': user.profile_picture_id
                },
                'title': post.title,
                'publishedOn': post.created_on.isoformat(),
                'quotes': json.JSONDecoder().decode(post.content),
                'commentsCount': comment_count,
                'likesCount': like_count,
                'isLiked': is_liked_by_user
            }
            explore_posts.append(post_info)
        explore_posts.sort(
            key=lambda x: x['likesCount'],
            reverse=True
        )
        api_response = {
            'success': True,
            'data': paginate_list(
                explore_posts,
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
