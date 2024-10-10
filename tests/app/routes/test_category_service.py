import unittest
from app import create_app, mongo
from config import TestingConfig


class CategoryServiceTestCase(unittest.TestCase):
    def setUp(self):
        self.app = create_app(TestingConfig)
        self.client = self.app.test_client()
        self.db = mongo.db

    def tearDown(self):
        self.db.drop_collection('categories')
        self.db.drop_collection('users')
        mongo.cx.close()

    def test_get_subcategories(self):
        self.db.categories.insert_many([
            {'_id': 'cat_1', 'name': 'Category 1', 'parent_id': None},
            {'_id': 'cat_2', 'name': 'Category 2', 'parent_id': 'cat_1'}
        ])
        response = self.client.get('/categories?parent_id=cat_1')
        self.assertEqual(response.status_code, 200)
        self.assertTrue(response.json['type'], 'category')
        self.assertEqual(len(response.json['subcategories']), 1)

    def test_get_users_in_last_category(self):
        self.db.categories.insert_one({'_id': 'cat_3', 'name': 'Category 3', 'parent_id': 'cat_2'})
        self.db.users.insert_many([
            {'_id': 'user_1', 'name': 'User 1', 'category_id': 'cat_3'},
            {'_id': 'user_2', 'name': 'User 2', 'category_id': 'cat_3'}
        ])
        response = self.client.get('/categories?parent_id=cat_3')
        self.assertEqual(response.status_code, 200)
        self.assertTrue(response.json['type'], 'user')
        self.assertEqual(len(response.json['users']), 2)

    def test_get_no_subcategories_or_users(self):
        self.db.categories.insert_one({'_id': 'cat_5', 'name': 'Category 4', 'parent_id': 'cat_3'})
        response = self.client.get('/categories?parent_id=cat_5')
        self.assertEqual(response.status_code, 404)
        self.assertIn('message', response.json)

if __name__ == '__main__':
    unittest.main()