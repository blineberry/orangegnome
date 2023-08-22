# Generated by Django 4.2.3 on 2023-08-21 00:12

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('feed', '0009_alter_feeditem_published'),
    ]

    operations = [
        migrations.CreateModel(
            name='Like',
            fields=[
                ('feeditem_ptr', models.OneToOneField(auto_created=True, on_delete=django.db.models.deletion.CASCADE, parent_link=True, primary_key=True, serialize=False, to='feed.feeditem')),
                ('url', models.URLField()),
            ],
            options={
                'abstract': False,
            },
            bases=('feed.feeditem',),
        ),
    ]