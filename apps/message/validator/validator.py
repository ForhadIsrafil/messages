from bandwidth.models import CallbackURLInfo
from django.conf import settings


def validate_number(number):
    if number is not None:
        number = number.replace('(', '').replace(')', '').replace('-', '').replace(' ', '')

    if not number.startswith('+1'):
        number = '+1' + number

    if len(number) != 12:
        return False

    return number


def get_callback_url(user_id):
    callback_info = CallbackURLInfo.objects.filter(user_id=user_id).first()
    if callback_info is not None:
        callback_url = callback_info.url
    else:
        callback_url = settings.SMS_CALLBACKURL
    return callback_url


def make_headers():
    headers = {
        'content-type': 'application/json',
        'Authorization': settings.BANDWIDTH_AUTHORIZATION
    }
    return headers
