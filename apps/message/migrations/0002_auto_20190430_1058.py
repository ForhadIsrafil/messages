# Generated by Django 2.1.1 on 2019-04-30 10:58

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('message', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='MMSLink',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('link', models.CharField(max_length=150)),
            ],
        ),
        migrations.AddField(
            model_name='message',
            name='type',
            field=models.CharField(default='sms', max_length=20),
        ),
        migrations.AddField(
            model_name='mmslink',
            name='message',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='message.Message'),
        ),
    ]