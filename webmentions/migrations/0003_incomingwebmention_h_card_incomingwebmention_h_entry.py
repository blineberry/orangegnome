# Generated by Django 4.2.3 on 2023-08-10 02:10

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('webmentions', '0002_incomingwebmention_target_and_more'),
    ]

    operations = [
        migrations.AddField(
            model_name='incomingwebmention',
            name='h_card',
            field=models.TextField(null=True),
        ),
        migrations.AddField(
            model_name='incomingwebmention',
            name='h_entry',
            field=models.TextField(null=True),
        ),
    ]
