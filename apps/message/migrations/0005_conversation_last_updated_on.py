# Generated by Django 2.1.1 on 2019-05-23 18:55

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('message', '0004_auto_20190509_1647'),
    ]

    operations = [
        migrations.AddField(
            model_name='conversation',
            name='last_updated_on',
            field=models.DateTimeField(auto_now=True),
        ),
    ]