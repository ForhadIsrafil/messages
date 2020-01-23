from message.models import Conversation, Message, MessageSendMap, MessageReceivedMap, UserNumber, \
    TrackExternalConversation, \
    ExternalNumber, MMSLink
from urllib.parse import urljoin
from os.path import join as pathjoin
import os
import uuid
import requests
from django.conf import settings
from message.models import Message, MessageSendMap, TrackExternalConversation, \
    ExternalNumber

from message.models import MMSLink
from apps.message.send_message_utils.enum import MessageTypeEnum

THUMBNAIL_SIDE_LIMIT = settings.THUMBNAIL_SIDE_LIMIT

from apps.message.validator.validator import make_headers


def save_received_message_maps(text, conversation_id, event_type=None, media=None):
    if media is None or media == []:
        message_instance = Message(text=text, conversation_id=conversation_id)
        message_instance.save()
    else:
        message_instance = Message(text=text, conversation_id=conversation_id, type=MessageTypeEnum.MMS.value)
        message_instance.save()

    message_send = MessageReceivedMap(message=message_instance)
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
