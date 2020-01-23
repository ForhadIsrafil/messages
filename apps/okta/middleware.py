import requests
from django.conf import settings
from okta.models import OktaUserInfo
from django.contrib.auth.models import User
import requests
from django.contrib.auth import authenticate
import django
from django.views.decorators.csrf import csrf_exempt
import json

try:
    from django.http import HttpResponse

except ImportError as exc:
    raise ImportError(
        "Couldn't import Django. Are you sure it's installed and "
        "available on your PYTHONPATH environment variable? Did you "
        "forget to activate a virtual environment?"
    ) from exc


@csrf_exempt
class OktaMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        setattr(request, '_dont_enforce_csrf_checks', True)

        skipped_path = ['/media/file', '/callback', '/get-access-token',
                        '/signup', '/signin', '/active-account', '/media/file/']

        for path in skipped_path:
            if path in request.META['PATH_INFO']:
                return self.get_response(request)

        token = request.META.get('HTTP_AUTHORIZATION')

        if token is None or token == '':
            return HttpResponse(json.dumps({'error': 'Authentication credential not given.'}), status=401)

        type, session_id = token.split()

        # checking if the user in DB
        req_user_info = OktaUserInfo.objects.filter(
            session_id=session_id).first()  # now here should be filtered sessiontoken

        if req_user_info:
            request.user = req_user_info.user
            request.user.save()
            return self.get_response(request)

        else:
            session_url = settings.OKTA_BASE_URL + "/api/v1/sessions/" + session_id
            session_headers = {
                "Accept": "application/json, text/javascript, */*; q=0.01",
                "Content-Type": "application/json",
                "Authorization": "SSWS " + settings.API_TOKEN,
                "Accept-Encoding": "gzip, deflate, br",
                "Accept-Language": "en-US,en;q=0.5"
            }
            data = {
                "sessionToken": session_id
            }
            session_response = requests.get(session_url, data={}, headers=session_headers)
            session_response_data = json.loads(session_response.content.decode('utf-8'))

            try:
                uid = session_response_data['userId']
            except:
                return HttpResponse(json.dumps({'error': 'Invalid token or token expired.'}), status=401)

            response = self.get_okta_user_info(uid)
            if response:
                check_response_data = response.json()

                okta_user = User.objects.filter(username=session_response_data['login']).first()
                if okta_user == None:
                    user = User(username=session_response_data['login'])
                    user.set_password(session_response_data['userId'])
                    user.save()

                    # saving okta access_token
                    info = OktaUserInfo(okta_user_id=uid)
                    info.user = user
                    info.session_id = session_response_data['id']
                    info.save()

                    # saving request.user
                    request.user = user
                    request.user.save()

                else:
                    # updating okta access token
                    info = OktaUserInfo.objects.get(user=okta_user)
                    info.session_id = session_response_data['id']
                    info.save()

                    # saving request.user
                    request.user = okta_user
                    request.user.save()

                return self.get_response(request)


            else:
                # Invalid token
                return HttpResponse(json.dumps(response), status=401)

    def get_okta_user_info(self, uid):
        check_url = settings.OKTA_BASE_URL + '/api/v1/apps/' + settings.OKTA_CLIENT_ID + '/users/' + uid

        check_headers = {
            "Accept": "application/json",
            "Content-Type": "application/x-www-form-urlencoded",
            "Authorization": "SSWS " + settings.API_TOKEN
        }
        response = requests.get(check_url, headers=check_headers)

        if response.status_code == 200:
            return response
        else:
            return False
