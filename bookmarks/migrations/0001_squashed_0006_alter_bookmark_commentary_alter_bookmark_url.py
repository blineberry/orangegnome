# Generated by Django 4.2.18 on 2025-02-07 14:01

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    replaces = [('bookmarks', '0001_initial'), ('bookmarks', '0002_bookmark_syndicate_to_mastodon_and_more'), ('bookmarks', '0003_alter_bookmark_url'), ('bookmarks', '0004_alter_bookmark_title'), ('bookmarks', '0005_alter_bookmark_commentary'), ('bookmarks', '0006_alter_bookmark_commentary_alter_bookmark_url')]

    initial = True

    dependencies = [
        ('feed', '0004_auto_20200417_2246_squashed_0009_alter_feeditem_published'),
    ]

    operations = [
        migrations.CreateModel(
            name='Bookmark',
            fields=[
                ('feeditem_ptr', models.OneToOneField(auto_created=True, on_delete=django.db.models.deletion.CASCADE, parent_link=True, primary_key=True, serialize=False, to='feed.feeditem')),
                ('url', models.CharField(default='', max_length=2000)),
                ('title', models.CharField(blank=True, max_length=100)),
                ('commentary', models.CharField(blank=True, default='', max_length=280)),
                ('quote', models.CharField(blank=True, max_length=280)),
                ('syndicate_to_mastodon', models.BooleanField(default=False)),
                ('syndicate_to_twitter', models.BooleanField(default=False)),
                ('syndicated_to_mastodon', models.DateTimeField(null=True)),
                ('syndicated_to_twitter', models.DateTimeField(null=True)),
            ],
            bases=('feed.feeditem',),
        ),
    ]
