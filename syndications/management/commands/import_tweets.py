from syndications.models import Tweet, TwitterUser
from notes.models import Note
import json
import argparse
import datetime
from django.core.management.base import BaseCommand, CommandError
from django.utils import timezone
from profiles.models import Profile
from feed.models import Tag

def has_media(tweet):
    if 'entities' not in tweet:
        return False

    if 'media' not in tweet['entities']:
        return False

    return True

def is_retweet(tweet):
    if 'full_text' not in tweet:
        return False
    
    if tweet['full_text'].startswith('RT @'):
        return True

    return False

def is_reply(tweet):
    return 'in_reply_to_user_id' in tweet

def has_links(tweet):
    if 'entities' not in tweet:
        return False

    if 'urls' not in tweet['entities']:
        return False

    return len(tweet['entities']['urls']) > 0

def add_tags(note, tweet):
    if 'entities' not in tweet:
        return note
    
    if 'hashtags' not in tweet['entities']:
        return note
    
    for hashtag in tweet['entities']['hashtags']:
        slug = hashtag['text']
        tags = Tag.objects.filter(slug=slug)
        
        if tags.exists():
            note.tags.add(tags[0])
            continue
        
        note.tags.create(
            name=slug,
            slug=slug,
        )

    return note

def import_tweet(tweet, user, author):
    created_at = datetime.datetime.strptime(tweet['created_at'], "%a %b %d %H:%M:%S %z %Y")

    note = Note.objects.create(
        content=tweet['full_text'],
        is_published=True,
        updated=timezone.now(),
        author=author,
        published=created_at,
        syndicated_to_twitter=created_at,
        syndicate_to_twitter=True,
    )

    note = add_tags(note, tweet)

    note.tweet.create(
        id_str=tweet['id_str'],
        created_at=created_at,
        user=user,
        full_text=tweet['full_text'],
    )

class Command(BaseCommand):
    help = 'Imports tweets from a Twitter archive'

    def add_arguments(self, parser):
        parser.add_argument('file', type=argparse.FileType('r'), help="A json file of archived tweets")
        parser.add_argument('screen_name', type=str, help="The Twitter screen name of the author of the archived tweets. (Needs to already exist in db)")

        parser.add_argument('--all', action="store_true", help="Import all tweets")
        parser.add_argument('--plain', action="store_true", help="Import plain tweets (no RTs, no replies, no media)")
        parser.add_argument('--media', action="store_true", help="Import plain tweets (no RTs, no replies, no media)")
        parser.add_argument('--replies', action="store_true", help="Import plain tweets (no RTs, no replies, no media)")
        parser.add_argument('--retweets', action="store_true", help="Import plain tweets (no RTs, no replies, no media)")
        parser.add_argument('--links', action="store_true", help="Import plain tweets (no RTs, no replies, no media)")
        parser.add_argument('--dryrun', action="store_true", help="Don't actually save anything")

    def handle(self, *args, **options):
        self.stdout.write(str(options['all']))
        self.stdout.write(str(options['plain']))

        user = TwitterUser.objects.get()
        author = Profile.objects.get(is_owner=True)

        data = options['file'].read()
        tweets = json.loads(data)
        media_tweets = list()
        retweets = list()
        replies = list()
        imports = list()
        links = list()
        from_og = list()    
        already_imported = list()    

        for tweet in tweets:
            if 'tweet' not in tweet:
                self.stdout.write('Tweet doesn\'t have "tweet"')

            t = tweet['tweet']

            if Tweet.objects.filter(id_str=t['id_str']):
                already_imported.append(t)
                self.stdout.write('Tweet was already imported')
                continue

            if t['source'] == "<a href=\"https://orangegnome.com\" rel=\"nofollow\">Orange Gnome</a>":
                from_og.append(t)
                self.stdout.write('Tweet was sent from Orange Gnome')
                continue

            if not options['links'] and has_links(t):
                links.append(t)
                self.stdout.write('Tweet has link(s) and --links was not passed')
                continue

            if not options['media'] and has_media(t):
                media_tweets.append(t)
                self.stdout.write('Tweet has media and --media was not passed')
                continue

            if not options['retweets'] and is_retweet(t):
                retweets.append(t)
                self.stdout.write('Tweet is retweet and --retweets was not passed')
                continue

            if not options['replies'] and is_reply(t):
                replies.append(t)
                self.stdout.write('Tweet is reply and --replies was not passed')
                continue

            imports.append(t)
            if not options['dryrun']:
                import_tweet(t, user, author)
            self.stdout.write('Tweet imported')

        self.stdout.write('%s tweets already imported' % len(already_imported))
        self.stdout.write('%s tweets originated from Orange Gnome' % len(from_og))
        self.stdout.write('%s tweets with links skipped' % len(links))
        self.stdout.write('%s tweets with media skipped' % len(media_tweets))
        self.stdout.write('%s retweets skipped' % len(retweets))
        self.stdout.write('%s replies skipped' % len(replies))
        self.stdout.write('%s tweets imported out of %s' % (len(imports), str(len(tweets))))

        if (len(already_imported) + len(from_og) + len(links) + len(media_tweets) + len(retweets) + len(replies) + len(imports)) == len(tweets):
            self.stdout.write('The match checks!')
        else:
            self.stdout.write('Uh oh the math does not check out')