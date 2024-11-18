# app/routes/view/forms.py
import asyncio
import urllib

from flask import Blueprint, request, redirect, url_for, flash, jsonify
from app.models.forms import Form
from app.utils.helpers.forms import send_email_to_all_staff

forms_bp = Blueprint('forms', __name__)

@forms_bp.route('/forms/go')
def go_forms():
    full_url = request.url

    url_index = full_url.find('?url=')
    if url_index == -1:
        flash({"title": "錯誤", "content": "無效的網址"}, "popup_error")
        return redirect(url_for('index.home'))

    url = full_url[url_index + len('?url='):]
    url = urllib.parse.unquote(url)

    uuid_index = full_url.find('&uuid=')
    if uuid_index == -1:
        flash({"title": "錯誤", "content": "無效的網址"}, "popup_error")
        return redirect(url_for('index.home'))

    uuid_start = uuid_index + len('&uuid=')
    uuid_end = full_url.find('&', uuid_start)
    if uuid_end == -1:  # if no other parameters after uuid
        uuid = full_url[uuid_start:]
    else:
        uuid = full_url[uuid_start:uuid_end]

    uuid = urllib.parse.unquote(uuid)

    form_id_index = full_url.find('&form_id=')
    if form_id_index == -1:
        flash({"title": "錯誤", "content": "無效的網址"}, "popup_error")
        return redirect(url_for('index.home'))

    form_id = full_url[form_id_index + len('&form_id='):]
    form_id = urllib.parse.unquote(form_id)

    form = Form.find_form_by_uuid(form_id)
    if form is None:
        flash({"title": "錯誤", "content": "無效的網址"}, "popup_error")
        return redirect(url_for('index.home'))

    if form.search_filled_by_user(uuid):
        flash({"title": "注意", "content": "表單已填寫過了！"}, "popup_error")
        return redirect(url_for('index.home'))

    return redirect(url)
