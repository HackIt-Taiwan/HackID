from flask import Blueprint, request, jsonify
from pymongo.errors import PyMongoError
from app import mongo
from app.utils.encryption import encrypt_data

sign_upload_bp = Blueprint('sign_upload', __name__)

@sign_upload_bp.route('/upload_signature', methods=['POST'])
def upload_signature():
    """
    Handle the user signature upload and mark the user as signed in.

    This function processes a POST request to upload a user's signature.
    The signature is saved to the database and the user's signed-in status
    is updated to True.

    :return: JSON response indicating success or error.
    :raises PyMongoError: If there is an issue with the database operation.
    :raises Exception: If an unexpected error occurs during the process.
    """
    try:
        data = request.get_json()
        user_id = data.get('user_id')
        signature = data.get('signature')

        if not data or 'user_id' not in data or 'signature' not in data:
            return jsonify({'message': 'Missing user_id or signature in request data'}), 400

        if not user_id or not signature:
            return jsonify({'message': 'Invalid user_id or signature'}), 400

        result = mongo.db.users.update_one(
            {'_id': user_id},  # Match the correct field for user ID
            {'$set': {'signature': encrypt_data(signature), 'signed_in': True}},
            upsert=True
        )

        if result.matched_count == 0:
            return jsonify({'message': 'User not found'}), 404

        return jsonify({'message': 'Signature upload successful'}), 200

    except PyMongoError as e:
        return jsonify({'message': 'Database error occurred', 'error': str(e)}), 5001

    except Exception as e:
        return jsonify({'message': 'An Unexpected error occurred', 'error': str(e)}), 5009
