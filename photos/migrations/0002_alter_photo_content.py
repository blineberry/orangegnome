# Generated by Django 4.1.3 on 2023-01-05 02:33

from django.db import migrations
import django_resized.forms
import photos.models
import photos.storage


class Migration(migrations.Migration):

    dependencies = [
        ('photos', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='photo',
            name='content',
            field=django_resized.forms.ResizedImageField(crop=None, force_format=None, keep_meta=True, quality=70, scale=None, size=[1188, 1188], storage=photos.storage.PublicAzureStorage, upload_to=photos.models.upload_to_callable),
        ),
    ]
