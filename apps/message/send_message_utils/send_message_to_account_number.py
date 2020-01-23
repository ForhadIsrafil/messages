import json
import requests
from apps.message.validator.validator import make_headers
from django.conf import settings


def send_to_account_number(data):
    headers = make_headers()
    send_request = requests.post(settings.MESSAGE_URL, data=json.dumps(data), headers=headers,
                                 auth=(settings.BANDWIDTH_API_TOKEN, settings.BANDWIDTH_API_SECRETE_KEY))
    return send_request
