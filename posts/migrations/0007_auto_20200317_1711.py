# Generated by Django 3.0.4 on 2020-03-17 17:11

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('profiles', '0001_squashed_0002_profile_twitter_screenname'),
        ('posts', '0006_auto_20200317_1709'),
    ]

    operations = [
        migrations.AlterField(
            model_name='post',
            name='author',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.PROTECT, to='profiles.Profile'),
        ),
        migrations.AlterField(
            model_name='post',
            name='published',
            field=models.DateTimeField(null=True),
        ),
    ]
