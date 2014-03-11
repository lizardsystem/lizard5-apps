import mock

from django.test import TestCase
from lizard_datasource import datasource
from lizard_datasource import location

from lizard_fancylayers import layers


class MockDataSource(datasource.DataSource):
    def locations(self, bare=True):
        return [location.Location('dummy', 0, 0)]

    def unit(self, choices_made=None):
        return None


@mock.patch('lizard_datasource.datasource.get_datasources',
            return_value=[MockDataSource()])
class TestAdapter(TestCase):
    def test_constructor_trivial(self, patched_datasource):
        workspace_item = mock.MagicMock()

        adapter = layers.FancyLayersAdapter(
            workspace_item,
            layer_arguments={'choices_made': "{}"})

        self.assertFalse(adapter.datasource is None)

    def test_html(self, patched_datasource):
        workspace_item = mock.MagicMock()

        adapter = layers.FancyLayersAdapter(
            workspace_item,
            layer_arguments={'choices_made': "{}"})

        html = adapter.html(identifiers=[{'identifier': 'dummy'}])

        self.assertTrue(html)

    def test_empty_legend(self, patched_datasource):
        # Don't return a legend if there are no annotations to grab colors
        # from.
        workspace_item = mock.MagicMock()

        adapter = layers.FancyLayersAdapter(
            workspace_item,
            layer_arguments={'choices_made': "{}"})

        legend = adapter.legend()
        self.assertEquals(legend, [])
