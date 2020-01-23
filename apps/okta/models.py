from django.db import models
from django.contrib.auth.models import User



class OktaUserInfo(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    okta_user_id = models.TextField()
    session_id = models.TextField(null=True, blank=True)

    class Meta:
        db_table = 'okta_info'
        app_label = 'okta'