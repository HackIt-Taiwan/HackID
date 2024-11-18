# app/utils/helpers/forms.py
import os
import time
from datetime import datetime, timedelta

import requests
import urllib.parse

from app.models.forms import Form
from app.models.staff import Staff
from app.utils.mail_sender import send_email


def create_form(form_data):
    form = Form(
        form_name=form_data['form_name'],
        form_url=form_data['form_url'],
        hidden_fields=form_data['hidden_fields'] if 'hidden_fields' in form_data else None,
        description=form_data['description'] if 'description' in form_data else None,
        form_type=form_data['form_type'],
        form_limit=form_data['form_limit'],
        form_time_deadline=form_data['form_time_deadline'] if 'form_time_deadline' in form_data else None
    )
    form.save()

    return form


async def send_email_to_all_staff(form_id, expiry_days=0):
    all_staff = Staff.objects()
    form = Form.find_form_by_uuid(form_id)

    for staff in all_staff:
        # if staff.email != "xiao.bo.nor@gmail.com":
        #     continue
        if not staff.email:
            continue

        query_params = {}
        if form.hidden_fields:
            for field in form.hidden_fields:
                if field == "uuid" and staff.uuid:
                    query_params["uuid"] = str(staff.uuid)
                elif field == "name" and staff.name:
                    query_params["name"] = staff.name
                elif field == "group" and staff.current_group:
                    query_params["group"] = staff.current_group

        query_params["form_id"] = form_id

        encoded_params = urllib.parse.urlencode(query_params, doseq=True)
        separator = '&' if '?' in form.form_url else '?&'
        personalized_url = f"{form.form_url}{separator}{encoded_params}"
        hackid_link = os.getenv("host_domain") + "/forms/go?url=" + personalized_url

        short_link = await make_short_link(hackid_link, expiry_days)
        if short_link:
            print(f"Sending email to {staff.name} ({staff.email}) with short link: {short_link}, URL: {hackid_link}")
            send_email(
                subject=f"[HackID] {form.form_name}",
                recipient=staff.email,
                template='emails/forms.html',
                name=staff.name,
                url=short_link,
            )
            form.add_sent_to_user(staff.uuid)
            time.sleep(3)
            pass

    print("已生成並發送所有郵件。")


async def make_short_link(url, expiry_days):

    if expiry_days == 0 or None:
        expiration_timestamp = None
    else:
        expiration_date = datetime.utcnow() + timedelta(days=expiry_days)
        expiration_timestamp = int(expiration_date.timestamp())

    headers = {
        'Authorization': f'Bearer {os.getenv("SHORTEN_API_TOKEN")}',
        'Content-Type': 'application/json'
    }
    if expiration_timestamp:
        payload = {
            "url": url,
            "expiration": expiration_timestamp
        }
    else:
        payload = {
            "url": url
        }

    response = requests.post(os.getenv("SHORTEN_API_URL"), headers=headers, json=payload)

    if response.status_code != 201:
        return None

    return "https://go.hackit.tw/" + response.json()['link']['slug']


# if __name__ == '__main__':
# form_data = {
#     'form_name': '(HackID)11.06 留存意願調查表',
#     'form_url': 'https://form.hackit.tw/form/0tASWFBT',
#     'hidden_fields': ['uuid', 'name', 'group'],
#     'description': '因組組織調整及延期規劃，固進行一次留存意願調查',
#     'form_type': '意願調查',
#     'form_limit': 1,
#     # 'form_time_deadline': '2022-01-01T00:00:00Z'
# }
#
# form = create_form(form_data)
# print(f'Created form: {form}')
