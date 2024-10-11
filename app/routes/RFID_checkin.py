from datetime import datetime, timezone

from flask import Blueprint, request, jsonify
from pymongo.errors import PyMongoError

from app import mongo

RFID_check_in_bp = Blueprint('RFID_check_in', __name__)

@RFID_check_in_bp.route('/rfid_checkin', methods=['POST'])
def rfid_checkin():
    try:
        data = request.get_json()
        user_id = data.get('user_id')
        evnet_id = data.get('event_id')

        if not user_id or not evnet_id:
            return jsonify({'message': 'Invalid user_id or evnet_id'}), 400

        mongo.db.checkins.update_one(
            {'user_id': user_id, 'event_id': evnet_id},
            {'$set': {
                'checked_in': True,
                'checkin_time': datetime.now(timezone.utc)
            }},
            upsert=True
        )

        return jsonify({'message': 'Check in successful'}), 200


    except PyMongoError as e:
        return jsonify({'message': 'Database error occurred', 'error': str(e)}), 5001

    except Exception as e:
        return jsonify({'message': 'An Unexpected error occurred', 'error': str(e)}), 5009