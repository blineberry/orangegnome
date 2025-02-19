# Generated by Django 3.0.4 on 2020-04-14 13:20

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('profiles', '0001_squashed_0002_profile_twitter_screenname'),
    ]

    operations = [
        migrations.CreateModel(
            name='Note',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('syndicated_to_twitter', models.DateTimeField(null=True)),
                ('syndicate_to_twitter', models.BooleanField(default=False)),
                ('is_published', models.BooleanField(default=False)),
                ('updated', models.DateTimeField(auto_now=True)),
                ('published', models.DateTimeField(null=True)),
                ('short_content', models.CharField(max_length=280)),
                ('author', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, to='profiles.Profile')),
            ],
            options={
                'abstract': False,
            },
        ),
    ]
