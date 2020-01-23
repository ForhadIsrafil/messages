from django.db import models
from django.conf import settings
from django.contrib.auth.models import User
import uuid
from datetime import datetime
from django.utils import timezone
from message.models import Conversation

class CallbackURLInfo(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    url = models.URLField(default=settings.SMS_CALLBACKURL)
