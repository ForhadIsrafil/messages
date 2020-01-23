from apps.message.send_message_utils.enum import MessageTypeEnum
from django.conf import settings
from rest_framework import status
import json
from rest_framework import serializers
from django.db import transaction
from message.models import MessageSendMap, Message, Conversation, MessageReceivedMap, MMSLink


class MessageSerializer(serializers.ModelSerializer):
    state = serializers.SerializerMethodField()
    message_from = serializers.SerializerMethodField()
    message_to = serializers.SerializerMethodField()
    media = serializers.SerializerMethodField()

    class Meta:
        model = Message
        fields = ('id', 'text', 'time', 'type', 'state', 'message_from', 'message_to', 'media')

    def get_state(self, object):
        is_exists = MessageSendMap.objects.filter(message_id=object.pk).exists()
        if is_exists:
            state = 'send'
        else:
            state = 'received'
        return state

    def get_message_from(self, object):
        message_from = Conversation.objects.filter(id=object.conversation.pk).first()
        return message_from.sender

    def get_message_to(self, object):
        message_to = Conversation.objects.filter(id=object.conversation.pk).first()
        return message_to.receiver

    def get_media(self, object):
        if object.type == MessageTypeEnum.MMS.value:
            links = MMSLink.objects.filter(message_id=object.pk).values_list('link', flat=True)
            return list(links)
        else:
            return None

