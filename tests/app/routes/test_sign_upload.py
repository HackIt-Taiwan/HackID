import unittest
from app import mongo, create_app
from app.utils.encryption import decrypt_data  # 引入解密函數
from config import TestingConfig


class SignatureUploadTestCase(unittest.TestCase):
    """
    Test case for the signature upload functionality,
    verifying both successful upload and encryption of the signature.
    """

    def setUp(self):
        """
        Set up the Flask app and insert a test user into the MongoDB collection.
        """
        self.app = create_app(TestingConfig)
        self.app_context = self.app.app_context()
        self.app_context.push()
        self.client = self.app.test_client()
        self.db = mongo.db

        self.db.users.insert_one({
            '_id': 'user_123',
            'name': 'Test User',
            'signed_in': False,
            'signature': None
        })

    def tearDown(self):
        """
        Clean up the users collection after each test.
        """
        self.db.users.drop()
        self.app_context.pop()

    def test_upload_signature(self):
        """
        Test the signature upload process, ensuring the signature is both stored
        and encrypted in the database, and that the user is marked as signed in.
        """
        signature_data = 'base64_encoded_signature'

        response = self.client.post('/upload_signature', json={
            'user_id': 'user_123',
            'signature': signature_data
        })

        self.assertEqual(response.status_code, 200)

        user = self.db.users.find_one({'_id': 'user_123'})

        self.assertTrue(user['signed_in'])

        self.assertNotEqual(user['signature'], signature_data)

        decrypted_signature = decrypt_data(user['signature'])
        self.assertEqual(decrypted_signature, signature_data)


if __name__ == '__main__':
    unittest.main()
