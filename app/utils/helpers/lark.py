# app/utils/helpers/lark.py
import os
import requests


def get_feishu_access_token():
    # Get the access token from Feishu
    token_response = requests.post(
        'https://open.feishu.cn/open-apis/auth/v3/tenant_access_token/internal/',
        json={'app_id': os.getenv("LARK_APP_ID"), 'app_secret': os.getenv("LARK_APP_SECRET")}
    )
    if token_response.status_code != 200:
        return None, 'Failed to retrieve access token'

    token_data = token_response.json()
    if token_data.get('code') != 0:
        return None, f"Access token retrieval failed: {token_data.get('msg')}"

    return token_data['tenant_access_token'], None


def get_department_id_by_group(group_name):
    # First, get the Feishu access token
    access_token, error_message = get_feishu_access_token()
    if not access_token:
        return False, None, error_message

    # Recursively search for the department matching group_name
    department_id, error_message = find_department_recursively(group_name, '0', access_token)
    if department_id:
        return True, department_id, None
    else:
        return False, None, error_message


def find_department_recursively(group_name, parent_department_id, access_token):
    """
    Recursively searches for the department matching the given group_name.
    :param group_name: The name of the department to find.
    :param parent_department_id: The ID of the parent department to search in (must use open_department_id).
    :param access_token: The Feishu access token.
    :return: The open_department_id if found, or None with an error message.
    """
    headers = {
        'Authorization': f'Bearer {access_token}',
        'Content-Type': 'application/json; charset=utf-8'
    }

    # Feishu API URL to list departments
    url = 'https://open.feishu.cn/open-apis/contact/v3/departments'
    params = {
        'user_id_type': 'user_id',
        'parent_department_id': parent_department_id  # Use open_department_id for parent
    }

    response = requests.get(url, headers=headers, params=params)

    if response.status_code != 200:
        return None, f"獲取部門列表失敗: {response.text}"

    department_data = response.json()
    if department_data.get('code') != 0:
        return None, f"獲取部門列表失敗: {department_data.get('msg')}"

    # Search for the department matching group_name in the current level
    departments = department_data['data']['items']
    for department in departments:
        if department['name'] == group_name:
            return department['open_department_id'], None

    # If no match is found, search recursively in the sub-departments
    for department in departments:
        sub_department_id, error_message = find_department_recursively(group_name, department['open_department_id'],
                                                                       access_token)
        if sub_department_id:
            return sub_department_id, None

    return None, '查無您所在的部門/組別'


def create_lark_user(data):
    # Get Feishu access token
    access_token, error_message = get_feishu_access_token()
    if not access_token:
        return False, None, error_message

    headers = {
        'Authorization': f'Bearer {access_token}',
        'Content-Type': 'application/json; charset=utf-8'
    }

    # Send a request to create the user in Feishu
    url = 'https://open.larksuite.com/open-apis/contact/v3/users'
    response = requests.post(url, json=data, headers=headers)

    response_data = response.json()

    if response_data.get('msg') != "success":
        return False, None, f"創建用戶失敗: {response_data.get('msg')}"

    lark_user_id = response_data['data']['user']['user_id']

    return True, lark_user_id, None
