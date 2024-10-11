import unittest
from app import create_app, mongo
from config import TestingConfig


class RFIDCheckInTestCase(unittest.TestCase):
    """
    Test case for the RFID-based check-in functionality,
    verifying successful check-in and proper database updates.
    """

    def setUp(self):
        """
        Set up the Flask app and insert a test user and event into the MongoDB collection.
        """
        self.app = create_app(TestingConfig)
        self.client = self.app.test_client()
        self.db = mongo.db

        self.db.users.insert_one({
            'user_id': 'user_123',
            'name': 'Test User'
        })
        self.db.events.insert_one({
            '_id': 'event_456',
            'name': 'Test Event'
        })

    def tearDown(self):
        """
        Clean up the users and events collections after each test.
        """
        self.db.users.drop()
        self.db.events.drop()
        self.db.checkins.drop()

    def test_rfid_check_in(self):
        """
        Test the RFID check-in process, ensuring the user is marked as checked in
        and that the check-in time is stored correctly in the database.
        """
        response = self.client.post('/rfid_checkin', json={
            'user_id': 'user_123',
            'event_id': 'event_456'
        })

        self.assertEqual(response.status_code, 200)

        checkin_record = self.db.checkins.find_one({
            'user_id': 'user_123',
            'event_id': 'event_456'
        })

        self.assertIsNotNone(checkin_record)
        self.assertTrue(checkin_record['checked_in'])
        self.assertIn('checkin_time', checkin_record)
        self.assertIsNotNone(checkin_record['checkin_time'])

if __name__ == '__main__':
    unittest.main()