# (c) Nelen & Schuurmans.  GPL licensed, see LICENSE.txt.
from django.conf.urls.defaults import *
from django.conf import settings
from django.contrib import admin
from lizard_ui.urls import debugmode_urlpatterns
from lizard_sticky_twitterized.views import StickyBrowserView

admin.autodiscover()

urlpatterns = patterns(
    '',
    url(r'^$',
        StickyBrowserView.as_view(),
        name='lizard_sticky_twitterized.sticky_browser'),
)

if getattr(settings, 'LIZARD_TWITTER_STANDALONE', False):
    admin.autodiscover()
    urlpatterns += patterns(
        '',
        (r'^map/', include('lizard_map.urls')),
        (r'^ui/', include('lizard_ui.urls')),
        (r'', include('staticfiles.urls')),
        (r'^admin/', include(admin.site.urls)),
    )

urlpatterns += debugmode_urlpatterns()
