# Generated by Django 2.1.1 on 2019-05-06 04:12

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('bandwidth', '0015_auto_20190505_1008'),
    ]

    operations = [
        migrations.AlterField(
            model_name='callbackurlinfo',
            name='url',
            field=models.URLField(default='http://fcacd5c2.ngrok.io/api/v1/callback'),
        ),
    ]
