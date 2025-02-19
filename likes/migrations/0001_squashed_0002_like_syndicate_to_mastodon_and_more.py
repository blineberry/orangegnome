# Generated by Django 4.2.18 on 2025-02-07 14:04

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    replaces = [('likes', '0001_initial'), ('likes', '0002_like_syndicate_to_mastodon_and_more')]

    initial = True

    dependencies = [
        ('feed', '0004_auto_20200417_2246_squashed_0009_alter_feeditem_published'),
    ]

    operations = [
        migrations.CreateModel(
            name='Like',
            fields=[
                ('feeditem_ptr', models.OneToOneField(auto_created=True, on_delete=django.db.models.deletion.CASCADE, parent_link=True, primary_key=True, serialize=False, to='feed.feeditem')),
                ('url', models.URLField()),
                ('syndicate_to_mastodon', models.BooleanField(default=False)),
                ('syndicated_to_mastodon', models.DateTimeField(null=True)),
            ],
            options={
                'abstract': False,
            },
            bases=('feed.feeditem',),
        ),
    ]
