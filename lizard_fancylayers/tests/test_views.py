import mock

from django.test import TestCase
from django.test import RequestFactory

from lizard_fancylayers import views


class TestHomepageView(TestCase):
    def setUp(self):
        self.view_function = views.HomepageView.as_view()

    def test_has_response(self):
        request = RequestFactory().get('/')
        request.session = mock.MagicMock()
        request.user = mock.MagicMock()

        response = self.view_function(request, '')
        print(help(self.assertContains))
        self.assertContains(response, 'Apps overview', status_code=200)
