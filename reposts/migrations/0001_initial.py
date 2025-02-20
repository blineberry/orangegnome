# Generated by Django 4.2.3 on 2023-08-22 16:19

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('feed', '0004_auto_20200417_2246_squashed_0009_alter_feeditem_published'),
    ]

    operations = [
        migrations.CreateModel(
            name='Repost',
            fields=[
                ('feeditem_ptr', models.OneToOneField(auto_created=True, on_delete=django.db.models.deletion.CASCADE, parent_link=True, primary_key=True, serialize=False, to='feed.feeditem')),
                ('syndicated_to_mastodon', models.DateTimeField(null=True)),
                ('syndicate_to_mastodon', models.BooleanField(default=False)),
                ('url', models.URLField(blank=True, null=True)),
                ('content', models.CharField(max_length=560)),
                ('source_author_name', models.CharField(default='Anonymous', max_length=200)),
                ('source_author_url', models.URLField(blank=True, null=True)),
            ],
            options={
                'abstract': False,
            },
            bases=('feed.feeditem', models.Model),
        ),
    ]
