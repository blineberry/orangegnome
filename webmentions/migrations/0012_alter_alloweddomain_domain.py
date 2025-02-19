# Generated by Django 4.2.18 on 2025-02-07 14:26

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('webmentions', '0001_squashed_0011_alloweddomain_unique_domain'),
    ]

    operations = [
        migrations.AlterField(
            model_name='alloweddomain',
            name='domain',
            field=models.CharField(help_text='The domain from which to auto-approve webmentions.', max_length=1000),
        ),
    ]
