from cryptography.fernet import Fernet
import os

# In a real app, this should be in an environment variable
# For now, we'll generate one or use a fixed one if provided
SECRET_KEY = Fernet.generate_key()
cipher_suite = Fernet(SECRET_KEY)

def encrypt_data(data: bytes) -> bytes:
    return cipher_suite.encrypt(data)

def decrypt_data(data: bytes) -> bytes:
    return cipher_suite.decrypt(data)

def get_secret_key():
    return SECRET_KEY
