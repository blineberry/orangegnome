# Generated by Django 4.1.3 on 2023-01-07 16:10

from django.db import migrations, models
import django_resized.forms
import photos.models
import photos.storage


class Migration(migrations.Migration):

    dependencies = [
        ('photos', '0003_rename_content_photo_image_photo_image_height_and_more'),
    ]

    operations = [
        migrations.AlterField(
            model_name='photo',
            name='caption',
            field=models.CharField(blank=True, max_length=560),
        ),
        migrations.AlterField(
            model_name='photo',
            name='image',
            field=django_resized.forms.ResizedImageField(crop=None, force_format=None, keep_meta=False, quality=70, scale=None, size=[1188, 1188], storage=photos.storage.PublicAzureStorage, upload_to=photos.models.upload_to_callable),
        ),
    ]
