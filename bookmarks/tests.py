from django.test import TestCase
from .models import Bookmark

# Create your tests here.
class BookmarkTest(TestCase):
    def test_newbookmark_renders_title_html(self):
        b = Bookmark(
            url="http://example.com", 
            title_md="Title")
        b.save()

        self.assertEqual("Title", b.title_html)

        b = Bookmark.objects.get(pk = b.pk)

        self.assertEqual("Title", b.title_md)
        self.assertEqual("Title", b.title_html)

    def test_newbookmark_renders_title_txt(self):
        b = Bookmark(
            url="http://example.com", 
            title_md="Title")
        b.save()

        self.assertEqual("Title", b.title_txt)

        b = Bookmark.objects.get(pk = b.pk)

        self.assertEqual("Title", b.title_md)
        self.assertEqual("Title", b.title_txt)

    def test_newbookmark_renders_quote_html(self):
        b = Bookmark(
            url="http://example.com", 
            quote_md="quote")
        b.render_commonmark_fields()
        b.save()

        self.assertEqual("<p>quote</p>\n", b.quote_html)

        b = Bookmark.objects.get(pk = b.pk)

        self.assertEqual("quote", b.quote_md)
        self.assertEqual("<p>quote</p>\n", b.quote_html)

    def test_newbookmark_renders_quote_txt(self):
        b = Bookmark(
            url="http://example.com", 
            quote_md="quote")
        b.render_commonmark_fields()
        b.save()

        self.assertEqual("quote", b.quote_txt)

        b = Bookmark.objects.get(pk = b.pk)

        self.assertEqual("quote", b.quote_md)
        self.assertEqual("quote", b.quote_txt)

    def test_newbookmark_renders_commentary_html(self):
        b = Bookmark(
            url="http://example.com", 
            commentary_md="commentary")
        b.render_commonmark_fields()
        b.save()

        self.assertEqual("<p>commentary</p>\n", b.commentary_html)

        b = Bookmark.objects.get(pk = b.pk)

        self.assertEqual("commentary", b.commentary_md)
        self.assertEqual("<p>commentary</p>\n", b.commentary_html)

    def test_newbookmark_renders_commentary_txt(self):
        b = Bookmark(
            url="http://example.com", 
            commentary_md="commentary")
        b.render_commonmark_fields()
        b.save()

        self.assertEqual("commentary", b.commentary_txt)

        b = Bookmark.objects.get(pk = b.pk)

        self.assertEqual("commentary", b.commentary_md)
        self.assertEqual("commentary", b.commentary_txt)