from django.db import migrations

def forwards_func(apps, schema_editor):
    Bookmark = apps.get_model("bookmarks", "Bookmark")
    db_alias = schema_editor.connection.alias
    
    for bookmark in Bookmark.objects.using(db_alias).filter(title_md="",commentary_md="",quote_md=""):
        bookmark.title_md = bookmark.title_txt
        bookmark.commentary_md = bookmark.commentary_txt
        bookmark.quote_md = bookmark.quote_txt
        bookmark.save()        

def reverse_func(apps, schema_editor):
    Bookmark = apps.get_model("bookmarks", "Bookmark")
    db_alias = schema_editor.connection.alias
    
    for bookmark in Bookmark.objects.using(db_alias).filter(title_md="",commentary_md="",quote_md=""):
        bookmark.title_txt = bookmark.title_md
        bookmark.commentary_txt = bookmark.commentary_md
        bookmark.quote_txt = bookmark.quote_md
        bookmark.save()   

class Migration(migrations.Migration):
    atomic = False
    dependencies = [
        ('bookmarks', '0011_bookmark_commentary_md_bookmark_quote_md_and_more')
    ]

    operations = [
        migrations.RunPython(forwards_func, reverse_func)
    ]