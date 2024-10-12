#!/usr/bin/python3
"""Module for endpoints management for comment on post"""
import re
import uuid
from sqlalchemy import and_
from datetime import datetime
from fastapi import APIRouter

from ..utils.navigation import paginate_list
from ..database import get_session, User, Comment
from ..form_types import CommentAddModel, CommentDeleteModel
from ..utils.token_management import AuthTokenMngr


endpoint = APIRouter(prefix='/api/v1')


@endpooint.get('/comment')
async def get_comment(id=''):
    """Create and return details if a certain comment"""
    api_response = {
        'success': False,
        'message': 'Comment not found.'
    }
    db_session = get_session()
    try:
        comment = db_session.query(Comment).filter(Comment.id == id).first()
        if comment:
            user = db_session.query(User).filter(
                User.id == comment.user_id
            ).first()
            if not user:
                return api_response
            comnt_rep = db_session.query(Comment).filter(
                Comment.comment_id == comment.id
            ).all()
            replies_c = len(comnt_rep) if comnt_rep else 0
            api_response = {
                'success': True,
                'data': {
                    'id': comment.id,
                    'user': {
                        'id': user.id,
                        'name': user.name,
                        'profilePictureId': user.profile_picture_id
                    },
                    'createdOn': comment.created_on.isoformat(),
                    'text': comment.content,
                    'postId': comment.post_id,
                    'repliesCount': replies_c,
                    'replyTo': comment.comment_id if comment.comment_id else ''
                }
            }
    finally:
        db_session.close()
    return api_response


@endpoint.get('/comments-of-post')
async def get_post_comments(id='', span='', after='', before=''):
    """Create and return all comments made under a post"""
    api_response = {
        'success': False,
        'message': 'Comments failed to be found.'
    }
    if not id:
        return api_response
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
        comments = db_session.query(Comment).filter(and_(
            Comment.post_id == id,
            Comment.comment_id == None
        )).all()
        comments_data = []
        if comments:
            for comment in comments:
                user = db_session.query(User).filter(
                    User.id == comment.user_id
                ).first()
                if not user:
                    continue
                comnt_reps = db_session.query(Comment).filter(and_(
                    Comment.post_id == id,
                    Comment.comment_id == comment.id
                )).all()
                replies_c = len(comnt_reps) if comnt_reps else 0
                comment_info = {
                    'id': comment.id,
                    'user': {
                        'id': user.id,
                        'name': user.name,
                        'profilePictureId': user.profile_picture_id
                    },
                    'createdOn': comment.created_on.isoformat(),
                    'text': comment.content,
                    'postId': comment.post_id,
                    'repliesCount': replies_c,
                    'replyTo': comment.comment_id if comment.comment_id else ''
                }
                comments_data.append(comment_info)
        comments_data.sort(
            key=lambda x: datetime.fromisoformat(x['createdOn'])
        )
        api_response = {
            'success': True,
            'data': paginate_list(
                comments_data,
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


@endpoint.get('/comment-replies')
async def get_comment_replies(id='', span='', after='', before=''):
    """Create and return the replies to a certain comment"""
    api_response = {
        'success': False,
        'message': 'Comment replies not found.'
    }
    if not id:
        return api_response
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
        comments = db_session.query(Comment).filter(
            Comment.comment_id == id
        ).all()
        replies_data = []
        if comments:
            for comment in comments:
                user = db_session.query(User).filter(
                    User.id == comment.user_id
                ).first()
                if not user:
                    continue
                comnt_reps = db_session.query(Comment).filter(and_(
                    Comment.post_id == id,
                    Comment.comment_id == comment.id
                )).all()
                replies_c = len(comnt_reps) if comnt_reps else 0
                replies_info = {
                    'id': comment.id,
                    'user': {
                        'id': user.id,
                        'name': user.name,
                        'profilePictureId': user.profile_picture_id
                    },
                    'createdOn': comment.created_on.isoformat(),
                    'text': comment.content,
                    'postId': comment.post_id,
                    'repliesCount': replies_c,
                    'replyTo': comment.comment_id if comment.comment_id else ''
                }
                replies_data.append(replies_info)
        replies_data.sort(
            key=lambda x: datetime.fromisoformat(x['createdOn'])
        )
        api_response = {
            'success': True,
            'data': paginate_list(
                replies_data,
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


@endpoint.get('/comments-by-user')
async def get_user_comments(id='', span='', after='', before=''):
    """Create and return all comments by a certain user"""
    api_response = {
        'success': False,
        'message': 'User id is required.'
    }
    if not id:
        return api_response
    api_response = {
        'success': False,
        'message': 'User comment not found.'
    }
    db_session = get_session()
    try:
        span = span.strip()
        if span and re.fullmatch(r'\d+', span) is None:
            api_response = {
                'success': False,
                'message': 'Invalid span type.'
            }
            return api_response
        span = int(span if span else '12')
        user = db_session.query(User).filter(User.id == id).first()
        if not user:
            return api_response
        comments = db_session.query(Comment).filter(
            Comment.user_id == id
        ).all()
        comments_data = []
        if comments:
            for comment in comments:
                comnt_reps = db_session.query(Comment).filter(
                    Comment.comment_id == comment.id
                ).all()
                replies_c = len(comnt_reps) if comnt_reps else 0
                comments_info = {
                    'id': comment.id,
                    'user': {
                        'id': user.id,
                        'name': user.name,
                        'profilePictureId': user.profile_picture_id
                    },
                    'createdOn': comment.created_on.isoformat(),
                    'text': comment.content,
                    'postId': comment.post_id,
                    'repliesCount': replies_c,
                    'replyTo': comment.comment_id if comment.comment_id else ''
                }
                comments_data.append(comments_info)
        comments_data.sort(
            key=lambda x: datetime.fromisoformat(x['createdOn'])
        )
        api_response = {
            'success': True,
            'data': paginate_list(
                comments_data,
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


@endpoint.post('/comment')
async def create_comment(body: CommentAddModel):
    """Generates and adds a new comment to a post"""
    api_response = {
        'success': False,
        'message': 'Failed to add comment.'
    }
    auth_token = AuthTokenMngr.convert_token(body.authToken)
    if auth_token is None or auth_token.user_id != body.userId:
        api_response['message'] = 'Invalid authentication token.'
        return api_response
    if len(body.content) > 384:
        api_response['message'] = 'Comment is too long.'
        return api_response
    db_session = get_session()
    try:
        reply_id = body.replyTo.strip() if body.replyTo else None
        if reply_id:
            queryres = db_session.query(Comment).filter(and_(
                Comment.id == reply_id,
                Comment.comment_id == None
            )).first()
            if not queryres or queryres.post_id != body.postId:
                db_session.close()
                return api_response
        gen_id = str(uuid.uuid4())
        currntdt = datetime.utcnow()
        comment = Comment(
            id=gen_id,
            created_on=currntdt,
            post_id=body.postId,
            user_id=body.userId,
            comment_id=reply_id,
            content=body.content
        )
        db_session.add(comment)
        db_session.commit()
        api_response = {
            'success': True,
            'data': {
                'id': gen_id,
                'createdOn': currntdt.isoformat(),
                'replyTo': body.replyTo if body.replyTo else '',
                'postId': body.postId,
                'repliesCount': 0
            }
        }
    except Exception as ex:
        print(ex.args[0])
        db_session.rollback()
    finally:
        db_session.close()
    return api_response


@endpoint.delete('/comment')
async def delete_comment(body: CommentDeleteModel):
    """Delete certain comment from a post"""
    api_response = {
        'success': False,
        'message': 'Comment delete failesd.'
    }
    auth_token = AuthTokenMngr.convert_token(body.authToken)
    if auth_token is None or auth_token.user_id != body.userId:
        api_response['message'] = 'Invalid authentication token.'
        return api_response
    db_session = get_session()
    try:
        db_session.query(Comment).filter(
            Comment.comment_id == body.commentId
        ).delete(
            synchronize_session=False
        )
        db_session.query(Comment).filter(
            Comment.id == body.commentId
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
