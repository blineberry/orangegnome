from django.test import TestCase
from feed.models import Tag
from .models import MastodonSyndicatable

# Create your tests here.
class MastodonSyndicatableTest(TestCase):
    def add_hashtags_substitutes_tags(self):
        status = "The quick brown fox jumps over the lazy dog."
        tags = list()
        tags.append(Tag(name="The Quick", slug="the-quick"))
        tags.append(Tag(name="Lazy Dog", slug="lazy-dog"))
        tags.append(Tag(name="red fox", slug="red-fox"))
        tags.append(Tag(name="jumps", slug="jumps"))

        status = MastodonSyndicatable.add_hashtags(status, tags)
        self.assertEqual(status, "#TheQuick brown fox #Jumps over the #LazyDog.\n\n#RedFox")