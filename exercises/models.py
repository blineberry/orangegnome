from django.db import models
from feed.models import FeedItem
from syndications.models import StravaActivity
from profiles.models import Profile

# Create your models here.
class Exercise(FeedItem):
    athlete = models.ForeignKey(Profile, on_delete=models.CASCADE)
    type = models.CharField(max_length=30)    
    distance = models.FloatField()
    moving_time = models.IntegerField()
    total_elevation_gain = models.FloatField()
    start_date = models.DateTimeField()
    start_date_local = models.DateTimeField()
    timezone = models.CharField(max_length=50)
    strava_activity = models.OneToOneField(StravaActivity, on_delete=models.PROTECT)
    comments = models.TextField(null=True)

    def feed_item_content(self):
        return self.comments

    def feed_item_header(self):
        return f'{self.start_date} {self.type}'

    def get_absolute_url(self):
        return 'absolute url'