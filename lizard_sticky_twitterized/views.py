# (c) Nelen & Schuurmans.  GPL licensed, see LICENSE.txt.
from lizard_map.views import AppView
from lizard_sticky_twitterized.models import StickyTweet


class StickyBrowserView(AppView):
    # hier de tweets van onderst. functie implementeren als functie
    # remco weet er meer van..

    def tweets(self):
        visible = StickyTweet.objects.filter(visible=True)
        #visible_with_image = visible.exclude(media_url__isnull=True).exclude(media_url__exact='').order_by('-created_on')
        return visible

    template_name = 'lizard_sticky_twitterized/sticky_twitterized-browser.html'
