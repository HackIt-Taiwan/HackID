import unittest
from app import create_app, mongo
from app.utils.encryption import encrypt_data
from config import TestingConfig


class CategoryServiceTestCase(unittest.TestCase):
    """
    Unit tests for the category service, focusing on encrypting user data
    and retrieving category/user information.
    """

    def setUp(self):
        """
        Set up the Flask app context and test client for each test.
        Push the app context to ensure proper app-level configurations are available.
        """
        self.app = create_app(TestingConfig)
        self.app_context = self.app.app_context()
        self.app_context.push()
        self.client = self.app.test_client()
        self.db = mongo.db

    def tearDown(self):
        """
        Clean up after each test by dropping the relevant collections
        and closing the MongoDB connection. Also pop the app context.
        """
        self.db.drop_collection('categories')
        self.db.drop_collection('users')
        mongo.cx.close()
        self.app_context.pop()

    def test_data_is_encrypted_in_db(self):
        """
        Test that user data is properly encrypted before being stored in the database.
        """
        encrypted_user_name = encrypt_data('User 1')

        self.db.users.insert_one({
            'user_id': 'user_1',
            'name': encrypted_user_name,
            'category_id': 'cat_1'
        })

        user = self.db.users.find_one({'user_id': 'user_1'})
        self.assertNotEqual(user['name'], 'User 1')

    def test_get_subcategories(self):
        """
        Test the retrieval of subcategories for a given parent category.
        """
        self.db.categories.insert_many([
            {'_id': 'cat_1', 'name': 'Category 1', 'parent_id': None},
            {'_id': 'cat_2', 'name': 'Category 2', 'parent_id': 'cat_1'}
        ])

        response = self.client.get('/categories?parent_id=cat_1')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json['type'], 'category')
        self.assertEqual(len(response.json['subcategories']), 1)

    def test_get_users_in_last_category(self):
        """
        Test the retrieval of users within a category, ensuring the user names are decrypted.
        """
        self.db.categories.insert_one({'_id': 'cat_3', 'name': 'Category 3', 'parent_id': 'cat_2'})
        self.db.users.insert_many([
            {
                'user_id': 'user_1',
                'name': encrypt_data('User 1'),
                'category_id': 'cat_3'
            },
            {
                'user_id': 'user_2',
                'name': encrypt_data('User 2'),
                'category_id': 'cat_3'
            }
        ])

        response = self.client.get('/categories?parent_id=cat_3')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json['type'], 'user')

        user_1_name = response.json['users'][0]['name']
        self.assertEqual(user_1_name, 'User 1')

        user_2_name = response.json['users'][1]['name']
        self.assertEqual(user_2_name, 'User 2')

        self.assertEqual(len(response.json['users']), 2)

    def test_get_no_subcategories_or_users(self):
        """
        Test that a category with no subcategories or users returns a 404 response.
        """
        self.db.categories.insert_one({'_id': 'cat_5', 'name': 'Category 4', 'parent_id': 'cat_3'})
        response = self.client.get('/categories?parent_id=cat_5')
        self.assertEqual(response.status_code, 404)
        self.assertIn('message', response.json)


if __name__ == '__main__':
    unittest.main()
