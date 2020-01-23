# Generated by Django 2.1.1 on 2019-04-12 08:26

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='Conversation',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('sender', models.CharField(max_length=50)),
                ('receiver', models.CharField(max_length=50)),
                ('is_active', models.BooleanField(default=True)),
            ],
            options={
                'db_table': 'conversation',
            },
        ),
        migrations.CreateModel(
            name='ExternalNumber',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('source', models.CharField(blank=True, max_length=50, null=True)),
                ('e164', models.CharField(blank=True, max_length=50, null=True)),
            ],
        ),
        migrations.CreateModel(
            name='Message',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('text', models.TextField()),
                ('time', models.DateTimeField(auto_now=True)),
                ('conversation', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='message.Conversation')),
            ],
            options={
                'db_table': 'message',
            },
        ),
        migrations.CreateModel(
            name='MessageReceivedMap',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('time', models.DateTimeField(auto_now=True)),
                ('state', models.CharField(default='received', max_length=10)),
                ('message', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='message.Message')),
            ],
            options={
                'db_table': 'message_received_map',
            },
        ),
        migrations.CreateModel(
            name='MessageSendMap',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('time', models.DateTimeField(auto_now=True)),
                ('state', models.CharField(default='send', max_length=10)),
                ('message', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='message.Message')),
            ],
            options={
                'db_table': 'message_send_map',
            },
        ),
        migrations.CreateModel(
            name='Number',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('number', models.CharField(max_length=50)),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'db_table': 'number',
            },
        ),
        migrations.CreateModel(
            name='TrackExternalConversation',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('sender', models.CharField(max_length=50)),
                ('receiver', models.CharField(max_length=50)),
                ('source', models.CharField(max_length=50)),
            ],
        ),
        migrations.AddField(
            model_name='externalnumber',
            name='number',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='message.Number'),
        ),
    ]
