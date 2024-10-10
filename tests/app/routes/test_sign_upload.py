import unittest
from app import mongo, create_app
from config import TestingConfig

class SignatureUploadTestCase(unittest.TestCase):
    def setUp(self):
        self.app = create_app(TestingConfig)
        self.client = self.app.test_client()
        self.db = mongo.db

        self.db.users.insert_one({
            '_id': 'user_123',
            'name': 'Test User',
            'signed_in': False,
            'signature': None
        })

    def tearDown(self):
        self.db.users.drop()

    def test_upload_signature(self):
        signature_data = 'base64_encoded_signature'

        response = self.client.post('/upload_signature', json = {
            'user_id': 'user_123',
            'signature': signature_data
        })

        self.assertEqual(response.status_code, 200)

        user = self.db.users.find_one({'_id': 'user_123'})
        self.assertEqual(user['signature'], signature_data)
        self.assertTrue(user['signed_in'])

if __name__ == '__main__':
    unittest.main()