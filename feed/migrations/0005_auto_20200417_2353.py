# Generated by Django 3.0.4 on 2020-04-18 03:53

from django.db import migrations

def up(apps, schema_editor):
    FeedItem = apps.get_model('feed', 'FeedItem')
    Post = apps.get_model('posts','Post')

    for item in FeedItem.objects.all():        
        if hasattr(item, 'post'):
            item.is_published = item.post.old_is_published
            item.published = item.post.old_published
            item.updated = item.post.old_updated
            item.author = item.post.old_author
            item.save()    

        if hasattr(item, 'note'):
            item.is_published = item.note.old_is_published
            item.published = item.note.old_published
            item.updated = item.note.old_updated
            item.author = item.note.old_author
            item.save() 

def down(apps, schema_editor):
    FeedItem = apps.get_model('feed', 'FeedItem')
    Post = apps.get_model('posts','Post')
    Note = apps.get_model('notes','Note')   

    for item in FeedItem.objects.all():  
        if hasattr(item, 'post'):
            post = Post.objects.get(pk=item.id)

            post.old_is_published = item.is_published
            post.old_published = item.published
            post.old_updated = item.updated
            post.old_author = item.author
            post.save()    

        if hasattr(item, 'note'):
            note = Note.objects.get(pk=item.id)

            note.old_is_published = item.is_published
            note.old_published = item.published
            note.old_updated = item.updated
            note.old_author = item.author
            note.save() 

class Migration(migrations.Migration):

    dependencies = [
        ('feed', '0004_auto_20200417_2246'),
        ('posts', '0029_auto_20200417_2244'),
        ('notes','0012_auto_20200417_2244')
    ]

    operations = [
        migrations.RunPython(up,down)
    ]
