from cryptography.fernet import Fernet

KEY = Fernet.generate_key()
cipher = Fernet(KEY)

def encrypt_data(data):
    """
    Encrypts the given string data using the Fernet cipher.

    :param data: The string data to be encrypted.
    :return: The encrypted data as a byte string.
    """
    return cipher.encrypt(data.encode())

def decrypt_data(encrypted_data):
    """
    Decrypts the given encrypted data using the Fernet cipher.

    :param encrypted_data: The encrypted byte string data to be decrypted.
    :return: The original string data after decryption.
    :raises InvalidToken: If the encrypted_data is invalid or tampered with.
    """
    return cipher.decrypt(encrypted_data).decode()
