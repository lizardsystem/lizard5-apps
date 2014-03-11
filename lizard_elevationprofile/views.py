# (c) Nelen & Schuurmans.  GPL licensed, see LICENSE.rst.
# -*- coding: utf-8 -*-
from __future__ import unicode_literals
from __future__ import print_function

from django.utils.translation import ugettext as _
from django.views.generic.base import View
from django.http import HttpResponse
from django.conf import settings
#from django.utils import simplejson as json

from lizard_map.views import MapView
from lizard_ui.layout import Action

import requests


class ElevationProfile(MapView):
    """
    Elevation Profile tmp stub
    """
    template_name = 'lizard_elevationprofile/elevationprofile.html'
    page_title = _('Elevation Profile')

    @property
    def content_actions(self):
        """
        Add button for elevation profile
        """
        actions = super(ElevationProfile, self).content_actions
        activate_elevationprofile = Action(
            name='',
            description=_('Draw a line to select an elevation profile'),
            url="javascript:void(null)",
            icon='icon-bar-chart',
            klass='map-elevationprofile')
        actions.insert(0, activate_elevationprofile)

        return actions


class ElevationData(View):
    def get(self, request, *args, **kwargs):
        """
        Get request linestring and srs, respond json elevation profile
        """
        srs = request.GET.get('srs')
        wkt_geom = request.GET.get('geom')
        url = settings.RASTERINFO_SERVER_URL
        params = {'srs': srs, 'geom': wkt_geom}
        r = requests.get(url, params=params)
        elevation_profile = r.text

        return HttpResponse(elevation_profile, content_type='application/json')
