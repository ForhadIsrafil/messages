from django.contrib.auth.models import User
from django.db import models

from apps.message.lib.clock import Clock
from apps.message.send_message_utils.enum import MessageTypeEnum


class UserNumber(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    number = models.CharField(max_length=50)

    class Meta:
        db_table = 'user_number'


class ExternalNumber(models.Model):
    number = models.ForeignKey(UserNumber, on_delete=models.CASCADE)
    source = models.CharField(max_length=50, null=True, blank=True)
    e164 = models.CharField(max_length=50, null=True, blank=True)  # cell phone number (+8801625789867)


class Conversation(models.Model):
    sender = models.CharField(max_length=50)
    receiver = models.CharField(max_length=50)
    last_updated_on = models.DateTimeField(default=Clock.utc_now())
    is_active = models.BooleanField(default=True)

    class Meta:
        db_table = 'conversation'


class TrackExternalConversation(models.Model):
    sender = models.CharField(max_length=50)
    receiver = models.CharField(max_length=50)
    source = models.CharField(max_length=50)


class Message(models.Model):
    type = models.CharField(default=MessageTypeEnum.SMS.value, max_length=20)
    text = models.TextField()
    time = models.DateTimeField(auto_now=True)
    conversation = models.ForeignKey(Conversation, on_delete=models.CASCADE)

    class Meta:
        db_table = 'message'

class MMSLink(models.Model):
    message = models.ForeignKey(Message, on_delete=models.CASCADE)
    link = models.CharField(max_length=150)


class MessageSendMap(models.Model):
    message = models.ForeignKey(Message, on_delete=models.CASCADE)
    time = models.DateTimeField(auto_now=True)
    state = models.CharField(max_length=10, default='send')

    class Meta:
        db_table = 'message_send_map'


class MessageReceivedMap(models.Model):
    message = models.ForeignKey(Message, models.CASCADE)
    time = models.DateTimeField(auto_now=True)
    state = models.CharField(max_length=10, default='received')

    class Meta:
        db_table = 'message_received_map'
