#!/usr/bin/python3
"""Module for user authentication endpoints management"""
import os
import uuid
import argon2
import email_validator
from sqlalchemy import and_
from fastapi import APIRouter
from datetime import datetime

from ..form_types import (
    SignInModel,
    SignUpModel,
    PasswordResetModel,
    PasswordResetRequestModel
)
from ..database import get_session, User
from ..utils.token_management import AuthTokenMngr, ResetTokenMngr
from ..utils.html_template_processor import html_template_render
from ..utils.mailing import deliver_message


endpoint = APIRouter(prefix='/api/v1')


@endpoint.post('/sign-in')
async def sign_in(body: SignInModel):
    """Verify user signin and generate an authentication token"""
    api_response = {
        'success': False,
        'message': 'Failed user authentication.'
    }
    db_session = get_session()
    try:
        email_validator.validate_email(body.email)
        user = db_session.query(User).filter(User.email == body.email).first()
        if user:
            max_login_attempts = int(os.getenv('APP_MAX_SIGNIN'))
            try:
                if user.signin_attempts >= max_login_attempts:
                    return api_response
                hashpwd = argon2.PasswordHasher()
                hashpwd.verify(user.hashed_password, body.password)
                if user.signin_attempts > 1:
                    db_session.query(User).filter(
                        user.email == body.email
                    ).update(
                        {
                            User.updated_on: datetime.utcnow(),
                            User.signin_attempts: 1
                        },
                        synchronize_session=False
                    )
                    db_session.commit()
                auth_token = AuthTokenMngr(
                    user_id=user.id,
                    email=user.email,
                    secure_text=user.hashed_password
                )
                api_response = {
                    'success': True,
                    'data': {
                        'userId': user.id,
                        'name': user.name,
                        'authToken': AuthTokenMngr.encode_token(auth_token)
                    }
                }
            except argon2.exceptions.VerificationError:
                active_account = user.user_active
                if user.signin_attempts + 1 == max_login_attempts:
                    active_account = False
                db_session.query(User).filter(User.email == body.email).update(
                    {
                        User.updated_on: datetime.utcnow(),
                        User.signin_attempts: user.signin_attempts + 1,
                        User.user_active: active_account
                    },
                    synchronize_session=False
                )
                db_session.commit()
                if not active_account:
                    deliver_message(
                        body.email,
                        'Your account has been locked',
                        html_template_render(
                            'locked_account',
                            name=user.name
                        )
                    )
    except Exception as ex:
        print(ex.args[0])
        db_session.rollback()
    finally:
        db_session.close()
    return api_response


@endpoint.post('/sign-up')
async def sign_up(body: SignUpModel):
    """Sign up new user and send welcome email"""
    api_response = {
        'success': False,
        'message': 'Account creation failed.'
    }
    try:
        email_validator.validate_email(body.email)
        if len(body.name) > 64:
            api_response['message'] = 'User name is too long.'
            return api_response
        db_session = get_session()
        hashpwd = argon2.PasswordHasher()
        try:
            deliver_message(
                body.email,
                'Welcome to Vita Experientia',
                html_template_render(
                    'welcome',
                    name=body.name
                )
            )
            phash = hashpwd.hash(body.password)
            gen_id = str(uuid.uuid4())
            currnttime = datetime.utcnow()
            new_user = User(
                id=gen_id,
                created_on=currnttime,
                updated_on=currnttime,
                name=body.name,
                email=body.email,
                hashed_password=phash
            )
            db_session.add(new_user)
            db_session.commit()
            auth_token = AuthTokenMngr(
                user_id=gen_id,
                email=body.email,
                secure_text=phash
            )
            api_response = {
                'success': True,
                'data': {
                    'userId': gen_id,
                    'name': body.name,
                    'authToken': AuthTokenMngr.encode_token(auth_token)
                }
            }
        except Exception as ex:
            print(ex.args[0])
            db_session.rollback()
            api_response = {
                'success': False,
                'message': 'Account creation failed.'
            }
        db_session.close()
    except email_validator.EmailNotValidError:
        api_response['message'] = 'Invalid email.'
    return api_response


@endpoint.post('/reset-password')
async def request_reset_password(body: PasswordResetRequestModel):
    """Get password reset token and send reset email"""
    api_response = {
        'success': False,
        'message': 'Token creation reset failed.'
    }
    db_session = get_session()
    try:
        email_validator.validate_email(body.email)
        queryres = db_session.query(User).filter(
            User.email == body.email
        ).first()
        if queryres:
            reset_token = ResetTokenMngr(
                user_id=quesryres.id,
                email=body.email,
                message='password_reset'
            )
            reset_token_str = ResetTokenMngr.encode_token(reset_token)
            db_session.query(User).filter(and_(
                User.id == queryres.id,
                User.email == body.email
            )).update(
                {
                    User.user_reset_token: reset_token_str
                },
                synchronize_session=False
            )
            db_session.commit()
            api_response = {
                'success': True,
                'data': {}
            }
            deliver_message(
                body.email,
                'Reset Your Password',
                html_template_render(
                    'password_reset',
                    name=queryres.name,
                    token=reset_token_str
                )
            )
    except Exception as ex:
        print(ex.args[0])
        db_session.rollback()
    finally:
        db_session.close()
    return api_response


@endpoint.put('/reset-password')
async def reset_password(body: PasswordResetModel):
    """User password using reset token updated"""
    api_response = {
        'success': False,
        'message': 'Password reset failed.'
    }
    db.session = get_session()
    try:
        email_validator.validate_email(body.email)
        user = db_session.query(User).filter(
            User.email == body.email
        ).first()
        reset_token = ResetTokenMngr.convert_token(body.resetToken)
        if not reset_token:
            return api_response
        if reset_token.has_expired():
            api_response = {
                'success': False,
                'message': 'Reset password token has expired.'
            }
            return api_response
        valid_condts[
            reset_token.email == body.email,
            len(body.password.strip()) > 8,
            reset_token.message == 'password_reset'
        ]
        if all(valid_condts):
            hashpwd = argon2.PasswordHasher()
            phash = hashpwd(body.password)
            db_session.query(User).filter(
                User.email == body.email
            ).update(
                {
                    User.hashed_password: phash,
                    User.user_reset_token: '',
                    User.signin_attempts: 1
                },
                synchronize_session=False
            )
            db_session.commit()
            auth_token = AuthTokenMngr(
                user_id=user.id,
                email=body.email,
                secure_text=phash
            )
            api_response = {
                'success': True,
                'data': {
                    'userId': user.id,
                    'name': user.name,
                    'authToken': AuthTokenMngr.encode_token(auth_token)
                }
            }
            deliver_message(
                body.email,
                'Your Password Has Been Changed',
                html_template_render(
                    'password_changed',
                    name=user.name
                )
            )
    except Exception as ex:
        print(ex.args[0])
        db_session.rollback()
    finally:
        db_session.close()
    return api_response
