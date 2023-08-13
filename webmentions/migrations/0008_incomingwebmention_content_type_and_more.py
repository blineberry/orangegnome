# Generated by Django 4.2.3 on 2023-08-12 01:07

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('contenttypes', '0002_remove_content_type_name'),
        ('webmentions', '0007_remove_incomingwebmention_content_type_and_more'),
    ]

    operations = [
        migrations.AddField(
            model_name='incomingwebmention',
            name='content_type',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='contenttypes.contenttype'),
        ),
        migrations.AddField(
            model_name='incomingwebmention',
            name='object_id',
            field=models.PositiveIntegerField(blank=True, null=True),
        ),
    ]
