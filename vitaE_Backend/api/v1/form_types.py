#!/usr/bin/python3
"""Module with data models for different API requests"""
from pydantic import BaseModel
from typing import Optional, List


class SignInModel(BaseModel):
    """Model for user sign in"""
    email: str
    password: str


class SignUpModel(BaseModel):
    """Model for user signup"""
    name: str
    email: str
    password: str


class PasswordResetRequestModel(BaseModel):
    """Model for password reset requests"""
    email: str


class PasswordResetModel(BaseModel):
    """Model for password reset"""
    email: str
    password: str
    resetToken: str


class UserDeleteModel(BaseModel):
    """Model to delete user account"""
    authToken: str
    userId: str


class UserUpdateModel(BaseModel):
    """Model to update user profile"""
    authToken: str
    userId: str
    name: str
    profilePicture: Optional[str]
    profilePictureId: str
    removeProfilePicture: bool
    email: str
    bio: str


class ConnectionModel(BaseModel):
    """Model to create user connection"""
    authToken: str
    userId: str
    followId: str


class PostAddModel(BaseModel):
    """Model to add new post"""
    authToken: str
    userId: str
    title: str
    quotes: List[str]


class PostUpdateModel(BaseModel):
    """Model to update post"""
    authToken: str
    userId: str
    postId: str
    title: str
    quotes: List[str]


class PostDeleteModel(BaseModel):
    """Model to delete a post"""
    authToken: str
    userId: str
    postId: str


class PostLikeModel(BaseModel):
    """Model to like a post"""
    authToken: str
    userId: str
    postId: str


class CommentAddModel(BaseModel):
    """Model to add a comment"""
    authToken: str
    userId: str
    postId: str
    content: str
    replyTo: Optional[str]


class CommentDeleteModel(BaseModel):
    """Model to delete a comment"""
    authToken: str
    userId: str
    commentId: str
