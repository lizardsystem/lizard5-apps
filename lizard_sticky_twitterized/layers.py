"""
Adapter for lizard-sticky-twitterized
"""
from __future__ import division, print_function
import os
import mapnik

from django.conf import settings
from django.contrib.gis.geos import Point
from django.contrib.gis.measure import D
from django.shortcuts import get_object_or_404
from django.template.loader import render_to_string

from lizard_map import workspace
from lizard_map.coordinates import WGS84
from lizard_map.coordinates import wgs84_to_google
from lizard_map.mapnik_helper import add_datasource_point
from lizard_map.models import ICON_ORIGINALS
from lizard_map.symbol_manager import SymbolManager
from lizard_sticky_twitterized.models import StickyTweet
from lizard_map.daterange import current_start_end_dates

ICON_STYLE = {'icon': 'twitter.png',
              'mask': ('twitter_mask.png', ),
              'color': (0.25, 0.6, 1, 0)}
              #Twitter blue


class AdapterStickyTwitterized(workspace.WorkspaceItemAdapter):

    def __init__(self, *args, **kwargs):
        """
        tags: list or queryset of tags

        If no tags are selected, all stickies are selected!
        """
        super(AdapterStickyTwitterized, self).__init__(*args, **kwargs)

    def style(self):
        """
        Make mapnik point style
        """
        symbol_manager = SymbolManager(
            ICON_ORIGINALS,
            os.path.join(settings.MEDIA_ROOT, 'generated_icons'))
        output_filename = symbol_manager.get_symbol_transformed(
            ICON_STYLE['icon'], **ICON_STYLE)
        output_filename_abs = os.path.join(
            settings.MEDIA_ROOT, 'generated_icons', output_filename)
        point_looks = mapnik.PointSymbolizer()
        point_looks.filename = output_filename_abs
        point_looks.allow_overlap = True
        layout_rule = mapnik.Rule()
        layout_rule.symbols.append(point_looks)
        point_style = mapnik.Style()
        point_style.rules.append(layout_rule)

        return point_style

    @property
    def stickies(self):
        """
        Return Stickies.
        """
        result = StickyTweet.objects.exclude(
            geom=None).exclude(visible=False)
        if self.layer_arguments:
            result = result.filter(id=self.layer_arguments['id'])
        return result

    def layer(self, layer_ids=None, request=None):
        """Return a layer with all stickies or stickies with selected
        tags
        """
        start_end = current_start_end_dates(request)
        layers = []
        styles = {}
        layer = mapnik.Layer("Stickies", WGS84)
        layer.datasource = mapnik.MemoryDatasource()
        stickies = self.stickies.exclude(time__gte=start_end[1]
                                         ).filter(time__gte=start_end[0])
        for _id, sticky in enumerate(stickies):
            add_datasource_point(layer.datasource,
                                 sticky.geom.x,
                                 sticky.geom.y,
                                 'Name',
                                 'hssd',
                                 _id)
        # generate "unique" point style name and append to layer
        style_name = "StickyTweets"
        styles[style_name] = self.style()
        layer.styles.append(style_name)

        layers = [layer, ]
        return layers, styles

    def values(self, identifier, start_date, end_date):
        """Return values in list of dictionaries (datetime, value, unit)
        """

        stickies = self.stickies.filter(datetime__gte=start_date,
                                        datetime__lte=end_date)
        return [{'datetime': sticky.datetime,
                 'value': sticky.description,
                 'unit': ''} for sticky in stickies]

    def search(self, google_x, google_y, radius=None):
        """
        returns a list of dicts with keys distance, name, shortname,
        google_coords, workspace_item, identifier
        """
        #from lizard_map.coordinates import google_to_rd
        #x, y = google_to_rd(google_x, google_y)
        #pnt = Point(x, y, srid=28992)  # 900913
        pnt = Point(google_x, google_y, srid=900913)  # 900913
        #print pnt, radius

        stickies = self.stickies.filter(
            geom__distance_lte=(pnt, D(m=radius * 0.5))).distance(pnt
                                                                  ).order_by('distance')

        if stickies:
            stickies = [stickies[0]]

        result = [{'distance': 0.0,
                   'name': '%s (%s)' % (sticky.tweet, sticky.twitter_name),
                   'shortname': str(sticky.tweet),
                   'object': sticky,
                   'google_coords': wgs84_to_google(sticky.geom.x,
                                                    sticky.geom.y),
                   'workspace_item': self.workspace_item,
                   'identifier': {'sticky_id': sticky.id},
                   } for sticky in stickies]
        return result

    def location(self, sticky_id, layout=None):
        """
        returns location dict.

        requires identifier_json
        """
        sticky = get_object_or_404(StickyTweet, pk=sticky_id)
        identifier = {'sticky_id': sticky.id}

        return {
            'name': '%s' % (sticky.twitter_name),
            'tweet': str(sticky.tweet),
            'media_url': str(sticky.media_url),
            'workspace_item': self.workspace_item,
            'identifier': identifier,
            'google_coords': wgs84_to_google(sticky.geom.x, sticky.geom.y),
            'object': sticky,
        }

    def symbol_url(self, identifier=None, start_date=None, end_date=None):
        return super(AdapterStickyTwitterized, self).symbol_url(
            identifier=identifier,
            start_date=start_date,
            end_date=end_date,
            icon_style=ICON_STYLE)

    def html(self, snippet_group=None, identifiers=None, layout_options=None):
        """
        Renders stickies
        """
        if snippet_group:
            snippets = snippet_group.snippets.all()
            identifiers = [snippet.identifier for snippet in snippets]
        display_group = [
            self.location(**identifier) for identifier in identifiers]
        add_snippet = False
        if layout_options and 'add_snippet' in layout_options:
            add_snippet = layout_options['add_snippet']
        return render_to_string(
            'lizard_sticky_twitterized/popup_sticky_twitterized.html',
            {'display_group': display_group,
             'add_snippet': add_snippet,
             'symbol_url': self.symbol_url()})
