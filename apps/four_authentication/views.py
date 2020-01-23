from django.shortcuts import render
import json
import requests
import uuid
from rest_framework.views import APIView
from rest_framework.viewsets import ViewSet
from rest_framework.response import Response
from rest_framework import status
import datetime

from django.conf import settings
from okta.models import OktaUserInfo
from django.db import transaction
from django.utils.decorators import method_decorator
from rest_framework import viewsets
from datetime import datetime
from .utils import Mailer
from django.db.models import Q
from itertools import chain
import random
import logging

logger = logging.getLogger(__name__)


class OktaSignup(ViewSet):
    @transaction.atomic
    def create(self, request, format=None):

        firstname = request.data.get('firstname').replace(' ', '')
        lastname = request.data.get('lastname').replace(' ', '')
        email = request.data.get('email').replace(' ', '')
        password = request.data.get('password').replace(' ', '')
        if firstname == '' or lastname == '' or email == '' or password == '':
            return Response({'error': 'Field can\'t be empty.All fields are required!'},
                            status=status.HTTP_400_BAD_REQUEST)

        url = settings.OKTA_BASE_URL + "/api/v1/users?activate=true"
        data = {
            "profile": {
                "firstName": firstname,
                "lastName": lastname,
                "email": email,
                "login": email
            },
            "credentials": {
                "password": {"value": password},
                "recovery_question": {
                    "question": "Who's a major player in the cowboy scene?",
                    "answer": "Annie Oakley"
                }
            },
            "groupIds": [
                settings.GROUP_ID
            ]
        }
        headers = {
            "Accept": "application/json, text/javascript, */*; q=0.01",
            "Content-Type": "application/json",
            "Authorization": "SSWS " + settings.API_TOKEN,
            # "Accept-Encoding": "gzip, deflate, br",
            "Accept-Language": "en-US,en;q=0.5"
        }
        response = requests.post(url, data=json.dumps(data), headers=headers)
        json_response = json.loads(response.content.decode('utf-8'))

        if response.status_code != 200:
            return Response(json.loads(response.content.decode('utf-8')), status=status.HTTP_400_BAD_REQUEST)

        mailer = Mailer()
        email_body = '<strong> Welcome to Telegents Family! </strong> <p>You’ve joined Telegents Family successfully.\
                    Please click given link below to activate your account.</p><p> Thank you </p>'

        email_body += settings.FRONTEND_URL + '/active-account?user=' + json_response['id']

        email_response = mailer.send_email(recipient=json_response['profile']['email'], message=email_body)
        if email_response is False:
            return Response({"error": "Email sending process failed."},
                            status=status.HTTP_500_INTERNAL_SERVER_ERROR)

        if response.status_code == 200:
            return Response(
                {'success': 'Your account is successfully created!.Please login'},
                status=status.HTTP_201_CREATED)
        else:
            return Response(json.loads(response.content.decode('utf-8')),
                            status=status.HTTP_400_BAD_REQUEST)


class OktaSignin(ViewSet):

    @transaction.atomic
    def create(self, request, format=None):
        username = request.data.get('email').replace(' ', '')
        password = request.data.get('password').replace(' ', '')
        if username == '' or password == '':
            return Response({'error': "'Field can't be empty.All fields are required!'"},
                            status=status.HTTP_400_BAD_REQUEST)

        url = settings.OKTA_BASE_URL + "/api/v1/authn"
        data = {
            "password": password,
            "username": username
        }
        headers = {
            "Accept": "application/json",
            "Content-Type": "application/json",
            "Authorization": "SSWS " + settings.API_TOKEN,
        }
        response = requests.post(url, data=json.dumps(data), headers=headers)

        if response.status_code == 200:
            response_data = json.loads(response.content.decode('utf-8'))
            session_token = response_data['sessionToken']

            session_url = settings.OKTA_BASE_URL + "/api/v1/sessions/"
            data = {
                "sessionToken": session_token
            }
            session_response = requests.post(session_url, data=json.dumps(data), headers=headers)

            session_response_data = json.loads(session_response.content.decode('utf-8'))
            response_data['sessionToken'] = session_response_data['id']

            return Response(response_data, status=status.HTTP_200_OK)
            # return Response(json.loads(response.content.decode('utf-8')), status=status.HTTP_200_OK)
        else:
            return Response(json.loads(response.content.decode('utf-8')),
                            status=status.HTTP_400_BAD_REQUEST)


class OktaLogout(ViewSet):

    def destroy(self, request):
        session_token = request.META.get('HTTP_AUTHORIZATION').strip()
        type, token = session_token.split()

        # okta_info = OktaUserInfo.objects.filter(access_token=token).first()
        okta_info = OktaUserInfo.objects.filter(session_id=token).first()

        if okta_info is None:
            return Response(status=status.HTTP_400_BAD_REQUEST)

        create_session_url = settings.OKTA_BASE_URL + "/api/v1/sessions/" + okta_info.session_id
        headers = {
            "Accept": "application/json",
            "Content-Type": "application/json",
            "Authorization": "SSWS " + settings.API_TOKEN
        }

        delete_session = requests.delete(create_session_url, data={},
                                         headers=headers)  # Closes a user’s session (logout).(for web)

        okta_info.access_token = None
        okta_info.session_id = None
        okta_info.save()
        return Response(status=status.HTTP_204_NO_CONTENT)


class ActivateUserAccount(ViewSet):
    @transaction.atomic
    def create(self, request, userid, format=None):
        activate_url = settings.OKTA_BASE_URL + '/api/v1/users/' + userid + '/lifecycle/activate?sendEmail=false'
        headers = {
            "Accept": "application/json",
            "Content-Type": "application/json",
            "Authorization": "SSWS " + settings.API_TOKEN
        }
        activate_response = requests.post(activate_url, data={}, headers=headers)
        if activate_response.status_code == 200:
            return Response({'success': 'Your account is successfully activated!.'}, status=status.HTTP_200_OK)
        else:
            return Response(json.loads(activate_response.content.decode('utf-8')), status=status.HTTP_400_BAD_REQUEST)
