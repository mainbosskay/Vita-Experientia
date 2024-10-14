#!/usr/bin/python3
"""Module for creating app secret key in base64"""
import os
import base64


def generate_app_key():
    """Create and converts app secret key to base 64"""
    key = os.urandom(32)
    key_base64 = base64.urlsafe_b64encode(key).decode('utf-8')
    return key_base64


if __name__ == "__main__":
    key = generate_app_key()
    print("APP Secret Key:", key)
