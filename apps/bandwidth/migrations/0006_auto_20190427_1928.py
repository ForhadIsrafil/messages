# Generated by Django 2.1.1 on 2019-04-27 19:28

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('bandwidth', '0005_auto_20190418_1734'),
    ]

    operations = [
        migrations.AlterField(
            model_name='callbackurlinfo',
            name='url',
            field=models.URLField(default='http://02c76101.ngrok.io/callback'),
        ),
    ]
