from django.contrib import admin
from lizard_sticky_twitterized.models import StickyTweet


class StickyTweetAdmin(admin.ModelAdmin):
    list_display = (
        '__unicode__', 'twitter_name', 'status_id', 'tweet',
        'media_url', 'visible', 'created_on', 'updated_on', 'geom', )


admin.site.register(StickyTweet, StickyTweetAdmin)
