# Generated by Django 3.0.4 on 2020-04-16 17:13

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('feed', '0001_squashed_0003_feeditem_tags'),
        ('notes', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='note',
            name='tags',
            field=models.ManyToManyField(related_name='notes', to='feed.Tag'),
        ),
    ]
