import unittest
from app import create_app, mongo
from config import TestingConfig

class CheckInTestCase(unittest.TestCase):
    def setUp(self):
        self.app = create_app(TestingConfig)
        self.client = self.app.test_client()
        self.db = mongo.db

    def tearDown(self):
        self.db.drop_collection('checkins')

    def test_user_checkin(self):
        response = self.client.post('/checkin', json = {
            'user_id': 'user_123',
            'event_id': 'evnet_456'
        })

        self.assertEqual(response.status_code, 200)

        checkin_record = self.db.checkins.find_one({
            'user_id': 'user_123',
            'event_id': 'evnet_456'
        })
        self.assertIsNotNone(checkin_record)
        self.assertTrue(checkin_record['checked_in'])

if __name__ == '__main__':
    unittest.main()