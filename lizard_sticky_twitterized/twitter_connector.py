#!/usr/bin/python
# (c) Nelen & Schuurmans.  GPL licensed.
from __future__ import division, print_function

from django.conf import settings
import urlparse
from twitter import *
from django.contrib.gis.geos import Point
from lizard_sticky_twitterized.models import StickyTweet
import locale
from datetime import datetime
from django.utils import timezone


def search_twitter(*args, **options):
    consumer_key = getattr(settings, 'CONSUMER_KEY')
    consumer_secret = getattr(settings, 'CONSUMER_SECRET')
    access_token = getattr(settings, 'ACCES_TOKEN')
    access_secret = getattr(settings, 'ACCES_SECRET')
    t = Twitter(auth=OAuth(access_token, access_secret,
                           consumer_key, consumer_secret))
    search_params = dict(q=args, count=100, geocode="52.09,5.10,160km",
                         result_type='recent', include_entities='1')
    tweets = t.search.tweets(**search_params)
    while tweets:
        for tweet in tweets.get('statuses'):
            writer = TweetWriter(tweet)
            writer.store()
        next_results = tweets['search_metadata'].get('next_results')
        if next_results:
            qs = next_results[1:]
            qs_dict = urlparse.parse_qs(qs, keep_blank_values=True)
            tweets = t.search.tweets(max_id=qs_dict['max_id'][0],
                                     **search_params)
        else:
            tweets = None
    delete_duplicates()


def delete_duplicates():
    for row in StickyTweet.objects.all():
        if StickyTweet.objects.filter(status_id=row.status_id).count() > 1:
            row.delete()


class TweetWriter():
    """
    Stores the content of a tweet if the tweet contains coordinates.
    Overwrites old tweets when the specified storage limit has been reached (default 300).
    """
    def __init__(self, tweet, limit=3000):
        self.tweet = tweet
        self.limit = limit

    def store(self):
        """
        Either stores geo-coded tweets as new entries or overwrites oldest
        """
        tweet = self.tweet
        if tweet.get('coordinates') is not None:
            if self._full():
                self._store_tweet(StickyTweet.objects.order_by('time')[0])
            else:
                self._store_tweet(StickyTweet())

    def _store_tweet(self, new_tweet):

        tweet = self.tweet
        new_tweet.twitter_name = tweet.get('user').get('screen_name')
        new_tweet.tweet = tweet.get('text')
        new_tweet.status_id = int(tweet.get('id'))
        new_tweet.geom = Point(
            float(tweet.get('coordinates').get('coordinates')[0]),
            float(tweet.get('coordinates').get('coordinates')[1])
        )
        new_tweet.time = self._tweet_time(tweet.get('created_at'))
        try:
            new_tweet.media_url = tweet.get('entities').get('media')[0].get(
                'media_url')
        except (AttributeError, TypeError):
            pass
        new_tweet.save()

    def _full(self):
        limit = self.limit-1
        if StickyTweet.objects.count() > limit:
            return True

    def _tweet_time(self, created_at):
        locale.setlocale(locale.LC_TIME, "en_US.utf8")
        time = datetime.strptime(created_at,
                                 '%a %b %d %H:%M:%S +0000 %Y')
        return timezone.make_aware(time, timezone.utc)
