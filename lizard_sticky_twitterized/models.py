# (c) Nelen & Schuurmans.  GPL licensed, see LICENSE.txt.

from django.contrib.gis.db import models


class StickyTweet(models.Model):
    """
    StickyTweet
    """
    twitter_name = models.CharField(blank=True, null=True, max_length=255)
    status_id = models.BigIntegerField(blank=True, null=True, max_length=255)
    tweet = models.CharField(blank=True, null=True, max_length=255)
    visible = models.BooleanField(default=True, help_text=u"Defines the site-wide visibility of the tweet")
    media_url = models.CharField(blank=True, max_length=255)
    time = models.DateTimeField(blank=True, null=True)

    created_on = models.DateTimeField(auto_now_add=True)
    updated_on = models.DateTimeField(auto_now=True)

    # geo stuff
    geom = models.PointField(blank=True, null=True)  # default srid 4326
    objects = models.GeoManager()

    def __unicode__(self):
        return u'%s' % self.tweet
