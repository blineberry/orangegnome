# Generated by Django 4.1.3 on 2023-01-07 14:54

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('photos', '0002_alter_photo_content'),
    ]

    operations = [
        migrations.RenameField(
            model_name='photo',
            old_name='content',
            new_name='image',
        ),
        migrations.AddField(
            model_name='photo',
            name='image_height',
            field=models.PositiveIntegerField(default=0),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='photo',
            name='image_width',
            field=models.PositiveIntegerField(default=0),
            preserve_default=False,
        ),
        migrations.AlterField(
            model_name='photo',
            name='caption',
            field=models.CharField(max_length=560),
        ),
    ]
