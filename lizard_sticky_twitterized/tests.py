# (c) Nelen & Schuurmans.  GPL licensed, see LICENSE.txt.

from django.test import TestCase
from lizard_sticky_twitterized.management import tweet_writer
from lizard_sticky_twitterized.models import StickyTweet

tweet_no_coordinates = {
    "id": 339373061935603713,
    "geo": None, "coordinates": None, "place": None, "contributors": None,
    "user": {'screen_name': "Test Tweeter"}}

tweet_with_coordinates = {
    "id": 339373064867442688,
    "coordinates": {"type": "Point", "coordinates": [-70.01739, 18.5339]},
    "user": {'screen_name': "Test Tweeter"}}


class HarvestTest(TestCase):

    def test_writer_class(self):
        writer = tweet_writer.TweetWriter(tweet_no_coordinates)
        self.assertEqual(writer.tweet.get("id"), 339373061935603713)

    def test_store_no_coordinates(self):
        writer = tweet_writer.TweetWriter(tweet_no_coordinates)
        writer.store()
        self.assertEqual(StickyTweet.objects.all().count(), 0)

    def test_store_with_coordinates(self):
        writer = tweet_writer.TweetWriter(tweet_with_coordinates)
        writer.store()
        self.assertEqual(StickyTweet.objects.all().count(), 1)

    def test_overwrite_with_more_than_limit(self):
        writer = tweet_writer.TweetWriter(tweet_with_coordinates, limit=3)
        for i in range(4):
            writer.store()
        self.assertEqual(StickyTweet.objects.all().count(), 3)
