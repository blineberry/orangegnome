from syndications.models import Tweet
from notes.models import Note
import json
import argparse
from django.core.management.base import BaseCommand, CommandError

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

def import_tweet(tweet):


class Command(BaseCommand):
    help = 'Imports tweets from a Twitter archive'

    def add_arguments(self, parser):
        parser.add_argument('file', type=argparse.FileType('r'))

        parser.add_argument('--all', action="store_true", help="Import all tweets")
        parser.add_argument('--plain', action="store_true", help="Import plain tweets (no RTs, no replies, no media)")
        parser.add_argument('--media', action="store_true", help="Import plain tweets (no RTs, no replies, no media)")
        parser.add_argument('--replies', action="store_true", help="Import plain tweets (no RTs, no replies, no media)")
        parser.add_argument('--retweets', action="store_true", help="Import plain tweets (no RTs, no replies, no media)")

    def handle(self, *args, **options):
        self.stdout.write(str(options['all']))
        self.stdout.write(str(options['plain']))

        data = options['file'].read()
        tweets = json.loads(data)
        media_tweets = list()
        retweets = list()
        replies = list()
        imports = list()
        from_og = list()        

        for tweet in tweets:
            if 'tweet' not in tweet:
                self.stdout.write('Tweet doesn\'t have "tweet"')

            t = tweet['tweet']

            if t['source'] == "<a href=\"https://orangegnome.com\" rel=\"nofollow\">Orange Gnome</a>":
                from_og.append(t)
                self.stdout.write('Tweet was sent from Orange Gnome')
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
            import_tweet(t)
            self.stdout.write('Tweet imported')

        self.stdout.write('%s tweets originated from Orange Gnome' % len(from_og))
        self.stdout.write('%s tweets with media skipped' % len(media_tweets))
        self.stdout.write('%s retweets skipped' % len(retweets))
        self.stdout.write('%s replies skipped' % len(replies))
        self.stdout.write('%s tweets imported out of %s' % (len(imports), str(len(tweets))))

        if (len(from_og) + len(media_tweets) + len(retweets) + len(replies) + len(imports)) == len(tweets):
            self.stdout.write('The match checks!')
        else:
            self.stdout.write('Uh oh the math does not check out')