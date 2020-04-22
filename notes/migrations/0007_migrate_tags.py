# Generated by Django 3.0.4 on 2020-04-18 02:27

from django.db import migrations

def up(apps, schema_editor):
    Note = apps.get_model('notes','Note')

    for note in Note.objects.all():
        note.feeditem.tags.set(note.tags.all())
        note.save()

def down(apps, schema_editor):
    Note = apps.get_model('notes','Note')

    for post in Note.objects.all():
        note.tags.set(note.feeditem.tags.all())
        note.save()

class Migration(migrations.Migration):

    dependencies = [
        ('notes', '0006_note_feeditem_ptr'),
    ]

    operations = [
        migrations.RunPython(up,down)
    ]
