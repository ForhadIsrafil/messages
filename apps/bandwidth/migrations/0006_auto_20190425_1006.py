# Generated by Django 2.1.1 on 2019-04-25 04:06

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('bandwidth', '0005_auto_20190418_1734'),
    ]

    operations = [
        migrations.AlterField(
            model_name='callbackurlinfo',
            name='url',
            field=models.URLField(default='http://fbf1cb76.ngrok.io/callback'),
        ),
    ]
