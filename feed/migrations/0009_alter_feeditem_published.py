# Generated by Django 4.2.3 on 2023-07-21 00:33

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('feed', '0008_remove_feeditem_is_published'),
    ]

    operations = [
        migrations.AlterField(
            model_name='feeditem',
            name='published',
            field=models.DateTimeField(blank=True, null=True),
        ),
    ]
