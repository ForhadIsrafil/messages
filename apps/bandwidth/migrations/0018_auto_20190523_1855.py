# Generated by Django 2.1.1 on 2019-05-23 18:55

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('bandwidth', '0017_auto_20190509_1028'),
    ]

    operations = [
        migrations.AlterField(
            model_name='callbackurlinfo',
            name='url',
            field=models.URLField(default='http://1b570882.ngrok.io/callback'),
        ),
    ]