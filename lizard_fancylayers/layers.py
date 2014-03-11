import datetime
import logging
import mapnik
import math
import os
import pytz

from django.conf import settings
from django.http import Http404
from django.template.loader import render_to_string

from lizard_map import coordinates
from lizard_map import workspace
from lizard_map.models import Setting

from lizard_map.adapter import Graph, FlotGraph
from lizard_map.adapter import adapter_serialize
from lizard_map.mapnik_helper import add_datasource_point
from lizard_map.models import ICON_ORIGINALS
from lizard_map.symbol_manager import SymbolManager

from lizard_datasource import properties
from lizard_datasource import datasource
from lizard_datasource import functools

logger = logging.getLogger(__name__)

DEFAULT_COLOR = '0000ff'
DEFAULT_SYMBOL_NAME = 'meetpuntPeil.png'
DEFAULT_SYMBOL_MASK = 'meetpuntPeil_mask.png'

# Used for graph lines after the first
COLORS = (
    'rgb(126, 209, 37)',  # Greenish, and needed for a project
    'rgb(255, 0, 0)',
    'rgb(0, 0, 255)',
    'rgb(0, 255, 255)',
    'rgb(255, 0, 255)',
    'rgb(255, 255, 0)'
)


def default_color():
    return Setting.get("FANCYLAYERS_DEFAULT_COLOR") or DEFAULT_COLOR


def default_symbol_name():
    return (Setting.get("FANCYLAYERS_DEFAULT_SYMBOL_NAME")
            or DEFAULT_SYMBOL_NAME).encode('utf8')


def default_symbol_mask():
    return (Setting.get("FANCYLAYERS_DEFAULT_SYMBOL_MASK")
            or DEFAULT_SYMBOL_MASK).encode('utf8')


@functools.memoize
def html_to_mapnik(color):
    if color[0] == '#':
        color = color[1:]

    r, g, b = color[0:2], color[2:4], color[4:6]
    rr, gg, bb = int(r, 16), int(g, 16), int(b, 16)

    return rr / 255.0, gg / 255.0, bb / 255.0, 1.0


def symbol_filename(color):
    symbol_manager = SymbolManager(
        ICON_ORIGINALS,
        os.path.join(settings.MEDIA_ROOT, 'generated_icons'))
    filename = symbol_manager.get_symbol_transformed(
        default_symbol_name(), mask=(default_symbol_mask(),),
        color=color)
    return filename


def symbol_pathname(color):
    filename = symbol_filename(color)
    pathname = os.path.join(
        settings.MEDIA_ROOT, 'generated_icons', filename)
    return pathname


def symbol_url(color):
    return "{media_url}generated_icons/{filename}".format(
        media_url=settings.MEDIA_URL, filename=symbol_filename(color))


class FancyLayersAdapter(workspace.WorkspaceItemAdapter):
    """Registered as adapter_fancylayers."""

    def __init__(self, *args, **kwargs):
        super(FancyLayersAdapter, self).__init__(*args, **kwargs)

        self.choices_made = datasource.ChoicesMade(
            json=self.layer_arguments['choices_made'])
        self.datasource = datasource.datasource(
            choices_made=self.choices_made)

    def layer(self, layer_ids=None, webcolor=None, request=None):
        # We only do point layers right now
        if not self.datasource.has_property(properties.LAYER_POINTS):
            return [], {}

        layers = []
        styles = {}

        locations = list(self.datasource.locations())
        colors = {"default": html_to_mapnik(default_color())}

        for location in locations:
            if location.color is not None:
                colors[location.color] = html_to_mapnik(location.color)

        style = mapnik.Style()

        for colorname, color in colors.iteritems():
            rule = mapnik.Rule()
            symbol = mapnik.PointSymbolizer()
            symbol.filename = symbol_pathname(color)
            symbol.allow_overlap = True
            rule.symbols.append(symbol)
            rule.filter = mapnik.Filter("[Color] = '{0}'".format(colorname))
            style.rules.append(rule)

        styles['trivialStyle'] = style

        layer = mapnik.Layer("Fancy Layers layer", coordinates.WGS84)
        layer.datasource = mapnik.MemoryDatasource()
        layer.styles.append('trivialStyle')

        for _id, location in enumerate(locations):
            color = location.color or 'default'
            add_datasource_point(
                layer.datasource, location.longitude,
                location.latitude,
                'Color', str(color), _id)

        layers.append(layer)
        return layers, styles

    def search(self, google_x, google_y, radius=None):
        """Return list of dict {'distance': <float>, 'timeserie':
        <timeserie>} of closest fews point that matches x, y, radius.
        """
        def distance(x1, y1, x2, y2):
            return math.sqrt((x2 - x1) ** 2 + (y2 - y1) ** 2)

        locations = self.datasource.locations()

        result = []
        for location in locations:
            x, y = coordinates.wgs84_to_google(
                location.longitude,
                location.latitude)
            dist = distance(google_x, google_y, x, y)

            if dist < radius:
                result.append(
                    {'distance': dist,
                     'name': location.description(),
                     'shortname': location.identifier,
                     'workspace_item': self.workspace_item,
                     'identifier': {'identifier': location.identifier},
                     'google_coords': (x, y),
                     'object': None})
        result.sort(key=lambda item: item['distance'])
        return result[:3]  # Max 3.

    def html(self, identifiers=None, layout_options=None):
        """Adapted version of lizard-map's html_default. If there are
        several graphs to be shown, we show them as several graphs in
        one popup tab."""
        is_collage = layout_options and layout_options.get('is_collage', False)

        # Build "adapter-image" url for current adapter and identifiers,
        # one for each identifier.
        urls = [
            {'image_url': self.workspace_mixin_item.url(
                    "lizard_map_adapter_image", [identifier]),
             'flot_url': self.workspace_mixin_item.url(
                    "lizard_map_adapter_flot_graph_data", [identifier]),
             'title': self.location(**identifier)['name']
             }
            for identifier in identifiers]

        # Makes it possible to create collage items from current
        # selected objects.
        collage_item_props = []
        # No export and selection for collages.
        if not is_collage:
            for identifier in identifiers:
                location = self.location(**identifier)
                collage_item_props.append(
                    {'name': location['name'],
                     'adapter_class': self.workspace_mixin_item.adapter_class,
                     'adapter_layer_json':
                         self.workspace_mixin_item.adapter_layer_json,
                     'identifier': adapter_serialize(identifier),
                     'url': self.workspace_mixin_item.url(
                            "lizard_map_adapter_values", [identifier, ],
                            extra_kwargs={'output_type': 'csv'})})

        render_kwargs = {
            'unit': u'',  # Don't show unit above the graphs
            'urls': urls,
            'symbol_url': self.symbol_url(),
            'collage_item_props': collage_item_props,
            'adapter': self,
            }

        if layout_options is not None:
            render_kwargs.update(layout_options)

        return render_to_string(
            'lizard_fancylayers/popup.html',
            render_kwargs)

    def symbol_url(self):
        # Note: it calls the symbol_url *function* in this module.
        return symbol_url(html_to_mapnik(DEFAULT_COLOR))

    def location(self, identifier, layout=None):
        locations = self.datasource.locations()
        for location in locations:
            if location.identifier == identifier:
                break
        else:
            return None

        google_x, google_y = coordinates.wgs84_to_google(
            location.longitude, location.latitude)

        identifier_to_return = {
            'identifier': identifier
            }
        if layout is not None:
            identifier_to_return['layout'] = layout

        description = location.description()

        return {
            'google_coords': (google_x, google_y),
            'name': description,
            'shortname': description,
            'workspace_item': self.workspace_item,
            'identifier': identifier_to_return,
            'object': location
            }

    def values(self, identifier, start_date, end_date):
        """Return values in list of dictionaries (datetime, value, unit)
        """
        timeseries = self.datasource.timeseries(
            identifier['identifier'], start_date, end_date)
        values = [{
                'datetime': data[0],
                'value': data[1],
                'unit': ""
                }
                for data in timeseries.data()
                ]

        return values

    def image(
        self, identifiers, start_date, end_date, width=380.0, height=250.0,
        layout_extra=None, raise_404_if_empty=False):
        # Initial version taken from lizard-fewsjdbc

        return self._render_graph(
            identifiers, start_date, end_date, width=width, height=height,
            layout_extra=layout_extra, raise_404_if_empty=raise_404_if_empty,
            GraphClass=Graph)

    def flot_graph_data(
        self, identifiers, start_date, end_date, layout_extra=None,
        raise_404_if_empty=False
    ):
        return self._render_graph(
            identifiers, start_date, end_date, layout_extra=layout_extra,
            raise_404_if_empty=raise_404_if_empty,
            GraphClass=FlotGraph)

    def _render_graph(
        self, identifiers, start_date, end_date, layout_extra=None,
        raise_404_if_empty=False, GraphClass=Graph, **extra_params
    ):
        """
        Visualize timeseries in a graph.

        Legend is always drawn.

        New: this is now a more generalized version of image(), to
        support FlotGraph.
        """

        def apply_lines(identifier, values, location_name):
            """Adds lines that are defined in layout. Uses function
            variable graph, line_styles.

            Inspired by fewsunblobbed"""

            layout = identifier['layout']

            if "line_min" in layout:
                graph.axes.axhline(
                    min(values),
                    color=line_styles[str(identifier)]['color'],
                    lw=line_styles[str(identifier)]['min_linewidth'],
                    ls=line_styles[str(identifier)]['min_linestyle'],
                    label='Minimum %s' % location_name)
            if "line_max" in layout:
                graph.axes.axhline(
                    max(values),
                    color=line_styles[str(identifier)]['color'],
                    lw=line_styles[str(identifier)]['max_linewidth'],
                    ls=line_styles[str(identifier)]['max_linestyle'],
                    label='Maximum %s' % location_name)
            if "line_avg" in layout and values:
                average = sum(values) / len(values)
                graph.axes.axhline(
                    average,
                    color=line_styles[str(identifier)]['color'],
                    lw=line_styles[str(identifier)]['avg_linewidth'],
                    ls=line_styles[str(identifier)]['avg_linestyle'],
                    label='Gemiddelde %s' % location_name)

        line_styles = self.line_styles(identifiers)

        locations = list(self.datasource.locations())
        today = datetime.datetime.now()

        graph = GraphClass(
            start_date, end_date, today=today,
            tz=pytz.timezone(settings.TIME_ZONE), **extra_params)
        graph.axes.grid(True)
#        parameter_name, unit = self.jdbc_source.get_name_and_unit(
#            self.parameterkey)
#        graph.axes.set_ylabel(unit)

        # Draw extra's (from fewsunblobbed)
        title = None
        y_min, y_max = None, None

        is_empty = True
        for identifier in identifiers:
            location_id = identifier['identifier']

            location_name = [
                location.description() for location in locations
                if location.identifier == location_id][0]

            timeseries = self.datasource.timeseries(
                location_id, start_date, end_date)

            if timeseries is not None:
                is_empty = False
                # Plot data if available.

                has_percentiles = False
                if (self.datasource.has_percentiles() and
                    hasattr(graph, 'add_percentiles')):
                    has_percentiles = True

                for series_num, series_name in enumerate(timeseries.columns):
                    series = timeseries.get_series(series_name)
                    dates = series.keys()
                    values = list(series)

                    # Hack -- show first line in normal color, every
                    # next line in green.  Because for the first
                    # practical use of this code, we have only one
                    # other line, and it must be green.
                    if series_num == 0:
                        color = line_styles[str(identifier)]['color']
                    else:
                        color = COLORS[(series_num - 1) % len(COLORS)]
                    if values:
                        # Percentiles have only one timeserie which
                        # needs the location label to add the percentiles.
                        label = timeseries.label(series_name)
                        if has_percentiles:
                            label = location_name

                        graph.axes.plot(
                            dates, values,
                            lw=1,
                            color=color,
                            label=label)

                # For the y-label, we take all the units that are not None,
                # each of them once only, and join them with ','
                units = []
                for column in timeseries.columns:
                    unit = timeseries.unit(column)
                    if unit is not None and unit not in units:
                        units.append(unit)
                if units:
                    graph.axes.set_ylabel(', '.join(units))

                if has_percentiles:
                    percentiles = self.datasource.percentiles(
                        location_id, start_date, end_date)
                    opacities = ()
                    if len(percentiles) == 2:
                        opacities = (0.4,)
                    elif len(percentiles) == 4:
                        opacities = (0.4, 0.2)

                    if opacities:
                        graph.add_percentiles(
                            location_name, percentiles, opacities)

            # Apply custom layout parameters.
            if 'layout' in identifier:
                layout = identifier['layout']
                if "y_label" in layout:
                    graph.axes.set_ylabel(layout['y_label'])
                if "x_label" in layout:
                    graph.set_xlabel(layout['x_label'])
                apply_lines(identifier, values, location_name)

        if is_empty and raise_404_if_empty:
            raise Http404

        # Originally legend was only turned on if layout.get('legend')
        # was true. However, as far as I can see there is no way for
        # that to become set anymore. Since a legend should always be
        # drawn, we simply put the following:
        graph.legend()

        # If there is data, don't draw a frame around the legend
        if graph.axes.legend_ is not None:
            graph.axes.legend_.draw_frame(False)
        else:
            # TODO: If there isn't, draw a message. Give a hint that
            # using another time period might help.
            pass

        # Extra layout parameters. From lizard-fewsunblobbed.
        y_min_manual = y_min is not None
        y_max_manual = y_max is not None
        if y_min is None:
            y_min, dummy = graph.axes.get_ylim()
        if y_max is None:
            dummy, y_max = graph.axes.get_ylim()

        if title:
            graph.suptitle(title)

        graph.set_ylim(y_min, y_max, y_min_manual, y_max_manual)

        # Copied from lizard-fewsunblobbed.
        if "horizontal_lines" in layout_extra:
            for horizontal_line in layout_extra['horizontal_lines']:
                graph.axes.axhline(
                    horizontal_line['value'],
                    ls=horizontal_line['style']['linestyle'],
                    color=horizontal_line['style']['color'],
                    lw=horizontal_line['style']['linewidth'],
                    label=horizontal_line['name'])

        graph.add_today()
        return graph.render()

    def legend(self, updates=None):
        """Returns a list of {'img_url':..., 'description':...}
        dictionaries that are used to make a legend for this
        datasource."""

        # If there is a legend, it is in the datasource's location annotations
        annotations = self.datasource.location_annotations() or {}

        if 'color' in annotations and annotations['color']:
            # Colorlegend is a list of (color, description) tuples
            colorlegend = annotations['color']
            return [{
                    'img_url': symbol_url(html_to_mapnik(color)),
                    'description': description}
                    for color, description in colorlegend]

        # If we cannot find any proper colored legend, return nothing.
        # This effectively hides the legend.
        return []
