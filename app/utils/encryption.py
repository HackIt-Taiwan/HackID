# app/utils/encryption.py
import os
import base64
import hashlib
import hmac
from Crypto.Cipher import AES
from Crypto.Util.Padding import pad, unpad
from Crypto.Random import get_random_bytes

AES_BLOCK_SIZE = 16  # AES block size for CBC mode


def _get_encryption_key():
    """Retrieve the AES-256 encryption key from the environment variables."""
    key = os.environ.get('ENCRYPTION_KEY')
    if not key:
        raise ValueError("ENCRYPTION_KEY is not set in the environment variables.")
    if len(key.encode()) < 32:
        raise ValueError("Encryption key must be at least 32 bytes (256 bits) for AES-256.")
    return key.encode()[:32]


def _get_hmac_key():
    """Retrieve the HMAC key from the environment variables (optional)."""
    hmac_key = os.environ.get('HMAC_KEY')
    if not hmac_key:
        raise ValueError("HMAC_KEY is not set in the environment variables.")
    return hmac_key.encode()


def aes_encrypt(data):
    """AES encrypt the data using a randomly generated IV each time for security."""
    key = _get_encryption_key()
    hmac_key = _get_hmac_key()

    # Generate IV
    iv = get_random_bytes(AES_BLOCK_SIZE)
    cipher = AES.new(key, AES.MODE_CBC, iv)

    # Encrypt data
    ct_bytes = cipher.encrypt(pad(data.encode(), AES_BLOCK_SIZE))

    # Generate HMAC for integrity verification
    mac = hmac.new(hmac_key, iv + ct_bytes, hashlib.sha256).digest()

    # Encode IV, ciphertext, and MAC as base64 strings
    iv_encoded = base64.urlsafe_b64encode(iv).decode('utf-8').rstrip('=')
    ct_encoded = base64.urlsafe_b64encode(ct_bytes).decode('utf-8').rstrip('=')
    mac_encoded = base64.urlsafe_b64encode(mac).decode('utf-8').rstrip('=')

    # Return the format iv:ciphertext:mac
    return f"{iv_encoded}:{ct_encoded}:{mac_encoded}"


def aes_decrypt(encrypted_data):
    """AES decrypt the data using the provided key and IV."""
    key = _get_encryption_key()
    hmac_key = _get_hmac_key()

    try:
        # Split encrypted data into IV, ciphertext, and MAC
        iv, ct, mac = encrypted_data.split(':')

        # Decode from base64
        iv = base64.urlsafe_b64decode(iv + '==')
        ct = base64.urlsafe_b64decode(ct + '==')
        mac = base64.urlsafe_b64decode(mac + '==')

        # Verify the HMAC for integrity
        expected_mac = hmac.new(hmac_key, iv + ct, hashlib.sha256).digest()
        if not hmac.compare_digest(mac, expected_mac):
            raise ValueError("MAC verification failed. Data has been tampered with.")

        # Perform AES decryption
        cipher = AES.new(key, AES.MODE_CBC, iv)
        pt = unpad(cipher.decrypt(ct), AES_BLOCK_SIZE)

        return pt.decode('utf-8')
    except (ValueError, KeyError) as e:
        raise ValueError(f"Decryption failed: {e}")


def hash_data(data):
    """Generate a SHA-256 hash of the given data."""
    return hashlib.sha256(data.encode('utf-8')).hexdigest()
