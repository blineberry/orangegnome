# Generated by Django 4.1.3 on 2022-12-10 02:33

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('contenttypes', '0002_remove_content_type_name'),
        ('syndications', '0013_mastodonstatus'),
    ]

    operations = [
        migrations.AddField(
            model_name='mastodonstatus',
            name='content_type',
            field=models.ForeignKey(default=0, on_delete=django.db.models.deletion.CASCADE, to='contenttypes.contenttype'),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='mastodonstatus',
            name='object_id',
            field=models.PositiveIntegerField(default=0),
            preserve_default=False,
        ),
    ]
