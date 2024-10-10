from cryptography.fernet import Fernet, InvalidToken
from flask import current_app

def get_cipher():
    """
    Retrieve the Fernet cipher using the FERNET_KEY from the application config.

    :return: A Fernet cipher instance.
    :raises ValueError: If the FERNET_KEY is not set in the configuration.
    """
    fernet_key = current_app.config.get('FERNET_KEY')
    if fernet_key is None:
        raise ValueError("FERNET_KEY is not set in the configuration.")
    return Fernet(fernet_key.encode())

def encrypt_data(data):
    """
    Encrypt the given data using the Fernet cipher.

    :param data: The string data to be encrypted.
    :return: The encrypted data as a base64-encoded string.
    """
    cipher = get_cipher()
    return cipher.encrypt(data.encode()).decode('utf-8')

def decrypt_data(encrypted_data):
    """
    Decrypt the given encrypted data using the Fernet cipher.

    :param encrypted_data: The encrypted base64-encoded string data to be decrypted.
    :return: The original string data after decryption.
    :raises ValueError: If the provided data is invalid or cannot be decrypted.
    """
    try:
        cipher = get_cipher()
        return cipher.decrypt(encrypted_data.encode('utf-8')).decode()
    except (InvalidToken, TypeError):
        raise ValueError("The provided data is not valid for decryption.")
