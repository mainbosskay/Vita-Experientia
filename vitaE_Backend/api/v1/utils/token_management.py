#!/usr/bin/python3
"""Module for validating and handling authentication token"""
import os
from json import JSONDecoder, JSONEncoder
from datetime import datetime, timedelta
from cryptography.fernet import Fernet

from ..database import get_session, User


class AuthTokenMngr:
    """Authenticating token manager for getting and verifying token"""
    def __init__(self, user_id='', email='', secure_text='', expires=None):
        """Initializing AuthTokenMngr class"""
        self.user_id = user_id
        self.email = email
        self.secure_text = secure_text
        if expires:
            self.expires = expires

    @property
    def user_id(self):
        """Create user id for AuthTokenMngr"""
        return self.__userId

    @user_id.setter
    def user_id(self, value):
        """Setting user id for AuthTokenMngr"""
        if type(value) is str:
            self.__userId = value
        else:
            raise TypeErroe('Invalid type.')

    @property
    def email(self):
        """Create email for AuthTokenMngr"""
        return self.__email

    @email.setter
    def email(self, value):
        """Setting email for AuthTokenMngr"""
        if type(value) is str:
            self.__email = value
        else:
            raise TypeError('Invalid Type.')

    @property
    def secure_text(self):
        """Create secure_text for AuthTokenMngr"""
        return self.__secureText

    @secure_text.setter
    def secure_text(self, value):
        """Setting secure text AuthTokenMngr"""
        if type(value) is str:
            self.__secureText = value
        else:
            raise TypeError('Invalid type.')

    @property
    def expires(self):
        """Create expiry date for AuthTokenMngr"""
        return self.__expiryDate

    @expires.setter
    def expires(self, value):
        """Sets the expiry date for AuthTokenMngr"""
        if type(value) is str:
            self.__expiryDate = datetime.fromisoformat(value)
        else:
            raise TypeError('Invalid type.')

    def has_expired(self):
        """Checking if the token generated has expired"""
        if not self.expires:
            return False
        currnttime = datetime.utcnow()
        expiry_conditions = [
            currnttime.year <= self.expires.year,
            currnttime.month <= self.expires.month,
            currnttime.day <= self.expires.day,
            currnttime.hour <= self.expires.hour,
            currnttime.minute <= self.expires.minute,
            currnttime.second <= self.expires.second
        ]
        return all(expiry_conditions)

    @staticmethod
    def convert_token(token: str):
        """Converting token string to an AuthTokenMngr object"""
        app_key = bytes(os.getenv('APP_SECRET_KEY'), 'utf-8')
        f = Fernet(app_key)
        db_session = get_session()
        try:
            decoded_token = JSONDecoder().decode(
                f.decrypt(bytes(token, 'utf-8')).decode('utf-8')
            )
            valid_keys = {
                'userId': str,
                'email': str,
                'secureText': str,
                'expires': str
            }
            if type(decoded_token) is not dict:
                raise TypeError('Decoded auth token should be a dictionary.')
            for key, val in decoded_token.items():
                if key in valid_keys:
                    if type(val) is not valid_keys[key]:
                        raise TypeError(
                            f'Auth token Key "{key}" has invalid type.')
                else:
                    raise KeyError(
                        f'Unexpected key "{key}" found in auth token.')
            currntdt = datetime.utcnow()
            expydt = datetime.fromisoformat(decoded_token['expires'])
            if currntdt >= expydt:
                raise ValueError('Auth token has expired.')
            user = db_session.query(User).filter(
                User.id == decoded_token['userId']
            ).first()
            valid_conds = (
                user is not None,
                user and user.user_active,
                user and user.email == decoded_token['email'],
                user and user.hashed_password == decoded_token['secureText']
            )
            if not all(valid_conds):
                raise ValueError(
                    'Auth token validation failed: data mismatch.')
            db_session.close()
            auth_token = AuthTokenMngr(
                user_id=decoded_token['userId'],
                email=decoded_token['email'],
                secure_text=decoded_token['secureText'],
                expires=decoded_token['expires']
            )
            return auth_token
        except Exception as ex:
            print(ex)
            db_session.close()
            return None

    @staticmethod
    def encode_token(auth_token) -> str:
        """Encode an AuthTokenMngr object to a token string"""
        app_key = bytes(os.getenv('APP_SECRET_KEY'), 'utf-8')
        f = Fernet(app_key)
        try:
            currntdt = datetime.utcnow()
            timedurr = timedelta(days=30)
            expydt = currntdt + timedurr
            encoded_text = JSONEncoder().encode(
                {
                    'userId': auth_token.user_id,
                    'email': auth_token.email,
                    'secureText': auth_token.secure_text,
                    'expires': expydt.isoformat()
                }
            )
            return f.encrypt(bytes(encoded_text, 'utf-8')).decode('utf-8')
        except Exception:
            return ''


class ResetTokenMngr:
    """Reset Token Manager class for validating and creating reset tokens"""
    def __init__(self, user_id='', email='', message='', expires=None):
        """Initializing ResetTokenMngr class"""
        self.user_id = user_id
        self.email = email
        self.message = message
        if expires:
            self.expires = expires

    @property
    def user_id(self):
        """Create user id for ResetTokenMngr"""
        return self.__userId

    @user_id.setter
    def user_id(self, value):
        """Setting user id for ResetTokenMngr"""
        if type(value) is str:
            self.__userId = value
        else:
            raise TypeError('Invalid type.')

    @property
    def email(self):
        """Create email for ResetTokenMngr"""
        return self.__email

    @email.setter
    def email(self, value):
        """Setting email for ResetTokenMngr"""
        if type(value) is str:
            self.__email = value
        else:
            raise TypeError('Invalid type.')

    @property
    def message(self):
        """Create message for ResetTokenMngr"""
        return self.__message

    @message.setter
    def message(self, value):
        """Setting message for ResetTokenMngr"""
        if type(value) is str:
            self.__message = value
        else:
            raise TypeError('Invalid type.')

    @property
    def expires(self):
        """Create expiry period for ResetTokenMngr"""
        return self.__expiryDate

    @expires.setter
    def expires(self, value):
        """Setting expiry period for ResetTokenMngr"""
        if type(value) is str:
            self.__expiryDate = datetime.fromisoformat(value)
        else:
            raise TypeError('Invalid type.')

    def has_expired(self):
        """Checking if the token generated has expired"""
        if not self.expires:
            return False
        currnttime = datetime.utcnow()
        expiry_conditions = [
            currnttime.year <= self.expires.year,
            currnttime.month <= self.expires.month,
            currnttime.day <= self.expires.day,
            currnttime.hour <= self.expires.hour,
            currnttime.minute <= self.expires.minute,
            currnttime <= self.expires.second
        ]
        return all(expiry_conditions)

    @staticmethod
    def convert_token(token: str):
        """Converting reset token string to ResetTokenMngr object"""
        app_key = bytes(os.getenv('APP_SECRET_KEY'), 'utf-8')
        f = Fernet(app_key)
        db_session = get_session()
        try:
            decoded_token = JSONDecoder().decode(
                f.decrypt(bytes(token, 'utf-8')).decode('utf-8')
            )
            valid_keys = {
                'userId': str,
                'email': str,
                'message': str,
                'expires': str
            }
            if type(decoded_token) is not dict:
                raise TypeError('Decoded reset token should be a dictionary.')
            for key, val in decoded_token.items():
                if key in valid_keys:
                    if type(val) is not valid_keys[key]:
                        raise TypeError(
                            f'Reset token key "{key}" has invalid type.')
                else:
                    raise KeyError(
                        f'Unexpected key "{key}" found in reset token')
            currntdt = datetime.utcnow()
            expydt = datetime.fromisoformat(decoded_token['expires'])
            if currntdt >= expydt:
                raise ValueError('Token has expired.')
            user = db_session.query(User).filter(
                User.id == decoded_token['id']
            ).first()
            valid_conds = (
                user is not None,
                user and user.user_active,
                user and user.email == decoded_token['email']
            )
            if not all(valid_conds):
                raise ValueError(
                    'Reset token validation failed: data mismatch')
            db_session.close()
            reset_token = ResetTokenMngr(
                user_id=decoded_token['userId'],
                email=decoded_token['email'],
                message=decoded_token['message']
            )
            reset_token.expires = decoded_token['expires']
            return reset_token
        except Exception:
            db_session.close()
            return None

    @staticmethod
    def encode_token(reset_token) -> str:
        """Encoding ResetTokenMngr object to a reset token string"""
        app_key = bytes(os.getenv('APP_SECRET_KEY'), 'utf-8')
        f = Fernet(app_key)
        try:
            currntdt = datetime.utcnow()
            timedurr = timedelta(days=30)
            expydt = currntdt + timedurr
            encoded_txt = JSONEncoder().encode(
                {
                    'id': reset_token.user_id,
                    'email': reset_token.email,
                    'message': reset_token.message,
                    'expires': expdt.isoformat()
                }
            )
            return f.encrypt(bytes(encoded_txt, 'utf-8')).decode('utf-8')
        except Exception:
            return ''
