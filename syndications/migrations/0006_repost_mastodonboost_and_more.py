# Generated by Django 4.2.3 on 2023-08-23 18:36

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('syndications', '0005_alter_reply_published'),
    ]

    operations = [
        migrations.CreateModel(
            name='Repost',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('repost_of_url', models.URLField()),
                ('author_name', models.CharField(blank=True, max_length=100, null=True)),
                ('author_url', models.URLField(blank=True, null=True)),
                ('author_photo', models.URLField(blank=True, null=True)),
                ('published', models.DateTimeField(blank=True, null=True)),
                ('url', models.URLField()),
            ],
        ),
        migrations.CreateModel(
            name='MastodonBoost',
            fields=[
                ('repost_ptr', models.OneToOneField(auto_created=True, on_delete=django.db.models.deletion.CASCADE, parent_link=True, primary_key=True, serialize=False, to='syndications.repost')),
                ('account_id_str', models.CharField(max_length=40)),
                ('boost_of_id_str', models.CharField(max_length=40)),
            ],
            bases=('syndications.repost',),
        ),
        migrations.AddConstraint(
            model_name='mastodonboost',
            constraint=models.UniqueConstraint(fields=('account_id_str', 'boost_of_id_str'), name='unique_mastodon_account_id_str_boost_of_id_str'),
        ),
    ]
