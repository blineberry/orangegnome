# Generated by Django 4.2.3 on 2023-08-17 20:00

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('webmentions', '0006_alter_incomingwebmention_options'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='incomingwebmention',
            name='type',
        ),
    ]
