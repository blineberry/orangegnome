# Generated by Django 4.2.18 on 2025-02-17 19:05

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('feed', '0010_syndication'),
    ]

    operations = [
        migrations.AlterField(
            model_name='feeditem',
            name='updated',
            field=models.DateTimeField(auto_now=True, null=True),
        ),
    ]
