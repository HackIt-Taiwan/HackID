from flask import Blueprint, request, jsonify
from pymongo.errors import PyMongoError
from app import mongo

category_bp = Blueprint('category', __name__)

@category_bp.route('/categories', methods=['GET'])
def get_subcategories_or_users():
    """
    Handle both subcategories and users based on the given parent_id.

    :param parent_id: The ID of the category to retrieve subcategories or users from.
    :return: JSON response with subcategories or users, and the type indicating which one.
    """
    parent_id = request.args.get('parent_id', None)

    try:
        subcategories = get_subcategories_by_parent_id(parent_id)
        if subcategories:
            return jsonify({'type': 'category', 'subcategories': subcategories}), 200

        users = get_users_by_category_id(parent_id)
        if users:
            return jsonify({'type': 'user', 'users': users}), 200

        return jsonify({'message': 'No subcategories or users found for this category'}), 404

    except PyMongoError as e:
        return jsonify({'message': 'Database error occurred', 'error': str(e)}), 5001

    except Exception as e:
        return jsonify({'message': 'An Unexpected error occurred', 'error': str(e)}), 5009


def get_subcategories_by_parent_id(parent_id):
    """
    Fetch subcategories based on parent_id from the database.

    :param parent_id: The ID of the parent category to search for subcategories.
    :return: A list of subcategories, or an empty list if none are found.
    """
    subcategories = list(mongo.db.categories.find({'parent_id': parent_id}))
    return [{'id': str(subcategory['_id']), 'name': subcategory['name']} for subcategory in subcategories]

def get_users_by_category_id(category_id):
    """
    Fetch users based on category_id from the database.

    :param category_id: The ID of the category to search for users.
    :return: A list of users, or an empty list if none are found.
    """
    users = list(mongo.db.users.find({'category_id': category_id}))
    return [{'id': str(user['_id']), 'name': user['name']} for user in users]