import json
import logging
import io
from urllib.parse import urljoin
from array import array
from mimetypes import guess_extension
from PIL import Image
import hashlib
import tempfile
import shutil
from os.path import join as pathjoin
import os
import uuid
import requests
from django.conf import settings
from message.models import Message, MessageSendMap, TrackExternalConversation, \
    ExternalNumber

from message.models import MMSLink
from apps.message.send_message_utils.enum import MessageTypeEnum
from apps.message.validator.validator import make_headers

THUMBNAIL_SIDE_LIMIT = settings.THUMBNAIL_SIDE_LIMIT

logger = logging.getLogger(__name__)


def save_send_message_maps(text, conversation_id, event_type=None, media=None):
    if media is None or media == []:
        message_instance = Message(text=text, conversation_id=conversation_id)
        message_instance.save()
    else:
        message_instance = Message(text=text, conversation_id=conversation_id, type=MessageTypeEnum.MMS.value)
        message_instance.save()

    message_send = MessageSendMap(message=message_instance)
    message_send.save()

    if event_type == MessageTypeEnum.MMS.value:
        headers = make_headers()
        for s_media in media:
            file_response = requests.get(s_media, data={}, headers=headers,
                                         auth=(settings.BANDWIDTH_API_TOKEN, settings.BANDWIDTH_API_SECRETE_KEY))

            if file_response.status_code == 200:
                ext = os.path.splitext(s_media)[-1]
                hash = str(uuid.uuid4())

                if ext == '.txt':
                    # here we need to save text
                    txt = file_response.content.decode("utf-8")
                    mms_msg= Message(text=txt, conversation_id=conversation_id,
                                               type=MessageTypeEnum.SMS.value)
                    mms_msg.save()
                    continue

                filename = hash + ext
                path = pathjoin(settings.FILE_ROOT, filename, )
                f = open(path, 'wb')
                f.write(file_response.content)
                f.close()

                host = settings.RUNNING_IP
                file_link = urljoin(host, '/media/file/' + filename)


                mms = MMSLink(message_id=message_instance.pk, link=file_link)
                mms.save()


def send_external(number_to_obj, actual_from_number, cell_numbers, message, callback_url, headers, media=None):
    send_sms_responses = []

    logger.info('number_to_obj id  %s', number_to_obj.pk)

    for cell_number in cell_numbers:

        pre_external = ExternalNumber.objects.filter(e164=cell_number, number_id=number_to_obj.pk).first()
        logger.info('pre_external id  %s', pre_external.pk)

        if media is None or media == []:
            data = {
                'from': pre_external.source,
                'to': cell_number,
                'text': actual_from_number + ' - ' + message,
                'callbackUrl': callback_url
            }
        else:
            data = {
                'from': pre_external.source,
                'to': cell_number,
                'text': actual_from_number + ' - ' + message,
                'callbackUrl': callback_url,
                'media': list(media)
            }
        url = 'https://api.catapult.inetwork.com/v1/users/u-lo5ohxwr4j3mro2vkmzcrka/messages/'

        send_sms_response = requests.post(url, data=json.dumps(data), headers=headers,
                                          auth=(settings.BANDWIDTH_API_TOKEN, settings.BANDWIDTH_API_SECRETE_KEY))

        if send_sms_response.status_code == 201:
            send_sms_responses.append(True)

            # This will be used when unknown user reply us
            ex_con = TrackExternalConversation(sender=actual_from_number, receiver=cell_number,
                                               source=pre_external.source)
            ex_con.save()
        else:
            logger.info("Error while sending message to external %s", send_sms_response.content)

    return True if False not in send_sms_responses else False


def _data(_from, to, text, callback_url, media=None):
    if media is None or media == []:
        data = {
            'from': _from,
            'to': to,
            'text': text,
            'callbackUrl': callback_url
        }
    else:
        data = {
            'from': _from,
            'to': to,
            'text': text,
            'media': list(media),
            'callbackUrl': callback_url
        }
    return data


# Here We were uploading a thumnail file (img)  and a ios file (model)

def upload_byte_file(file=None, model=None):
    filename = ''

    # Process the uploaded model
    _, ext = os.path.splitext(file.name)
    type = ext[1:].lower() if len(ext) > 0 else None

    with tempfile.NamedTemporaryFile(delete=False) as fp:
        tmppath = fp.name

        for chunk in file.chunks():
            fp.write(chunk)

        # Save the model in the static path
        hash = str(uuid.uuid4())
        filename = hash + '.' + type
        path = pathjoin(settings.FILE_ROOT, filename, )
        shutil.move(tmppath, path)

    return filename
