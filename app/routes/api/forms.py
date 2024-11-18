# app/routes/view/forms.py
from flask import Blueprint, request, jsonify
from app.models.forms import Form

forms_api_bp = Blueprint('forms_api', __name__)

@forms_api_bp.route('/forms/webhook', methods=['POST'])
def webhook():
    data = request.json

    uuid = None
    form_id = None
    if 'hiddenFields' in data:
        for field in data['hiddenFields']:
            if field.get('name') == 'uuid':
                uuid = field.get('value')
                continue
            if field.get('name') == 'form_id':
                form_id = field.get('value')
                continue

    with open('webhook_data.txt', 'w', encoding='utf-8') as f:
        f.write(f"Received data: {str(data)}\nExtracted UUID: {uuid}")

    print(f"Webhook received. Extracted UUID: {uuid}, Form ID: {form_id}")

    form = Form.find_form_by_uuid(form_id)
    if form is None:
        print('Form not found')
        return jsonify({'status': 'error', 'message': 'Form not found'}), 404
    form.add_filled_by_user(uuid)

    return jsonify({'status': 'ok', 'uuid': uuid}), 200
