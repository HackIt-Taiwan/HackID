# app/utils/request_utils.py
from flask import request
import ipaddress

def get_real_ip():
    """Retrieves the real IP address of the user."""
    ip_list = (
        request.headers.getlist("CF-Connecting-IP") or
        request.headers.getlist("X-Forwarded-For") or
        [request.remote_addr]
    )

    for ip in ip_list:
        ip = ip.strip()
        try:
            ip_obj = ipaddress.ip_address(ip)
            if isinstance(ip_obj, ipaddress.IPv4Address):
                return ip, 'IPv4'
        except ValueError:
            continue

    # If no IPv4 found, try IPv6
    for ip in ip_list:
        ip = ip.strip()
        try:
            ip_obj = ipaddress.ip_address(ip)
            if isinstance(ip_obj, ipaddress.IPv6Address):
                return ip, 'IPv6'
        except ValueError:
            continue

    return None, None
