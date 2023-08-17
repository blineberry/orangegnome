# Generated by Django 4.2.3 on 2023-08-15 19:50

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('webmentions', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='outgoingcontent',
            name='result',
            field=models.TextField(blank=True, default=''),
        ),
        migrations.AddField(
            model_name='outgoingcontent',
            name='tries',
            field=models.PositiveSmallIntegerField(default=0),
        ),
    ]