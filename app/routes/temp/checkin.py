from flask import Blueprint, request, jsonify
from datetime import datetime, timezone

from pymongo.errors import PyMongoError

from app import mongo

checkin_bp = Blueprint('checkin', __name__)

@checkin_bp.route('/checkin', methods=['POST'])
def check_in():
    """
    Process the check-in request, receive user_id and event_id, and store the check-in information in MongoDB.

    :return: JSON response with a success or error message.
    :raises: Various exceptions for invalid input or database errors.
    """
    try:
        data = request.get_json()
        if not data or 'user_id' not in data or 'event_id' not in data:
            return jsonify({'message': 'Missing user_id or event_id in request data'}), 400
        user_id = data['user_id']
        event_id = data['event_id']

        if not user_id or not event_id:
            return jsonify({'message': 'Invalid user_id or evnet_id'}), 400

        mongo.db.checkins.update_one(
            {'user_id': user_id, 'event_id': event_id},
            {'$set': {'checked_in': True, 'checkin_time': datetime.now(timezone.utc)}},
            upsert=True
        )

        return jsonify({'message': 'Check in successful'}), 200

    except PyMongoError as e:
        return jsonify({'message': 'Database error occurred', 'error': str(e)}), 5001

    except Exception as e:
        return jsonify({'message': 'An Unexpected error occurred', 'error': str(e)}), 5009