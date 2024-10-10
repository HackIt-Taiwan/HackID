import unittest
from cryptography.fernet import InvalidToken
from app.utils.encryption import encrypt_data, decrypt_data

class EncryptionTestCase(unittest.TestCase):
    def test_encrypt_data(self):
        original_data = 'Test Data'
        encrypted_data = encrypt_data(original_data)
        self.assertNotEqual(original_data, encrypted_data)
        self.assertTrue(len(encrypted_data) > 0)

    def test_decrypt_data(self):
        original_data = 'Test Data'
        encrypted_data = encrypt_data(original_data)
        decrypted_data = decrypt_data(encrypted_data)

        self.assertEqual(original_data, decrypted_data)

    def test_decrypt_invalid_data(self):
        with self.assertRaises(InvalidToken):
            decrypt_data("Invalid Encrypted Data")
