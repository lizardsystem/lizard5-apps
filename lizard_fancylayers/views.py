# (c) Nelen & Schuurmans.  GPL licensed, see LICENSE.rst.
from __future__ import unicode_literals

import logging

from django.core.urlresolvers import reverse
from django.utils import simplejson

from lizard_map.lizard_widgets import WorkspaceAcceptable
from lizard_map.views import AppView
from lizard_datasource import datasource

logger = logging.getLogger(__name__)


class FancyLayersView(AppView):
    # Placeholder for our own utils later
    pass


class HomepageView(FancyLayersView):
    template_name = 'lizard_fancylayers/homepage.html'

    def make_url(self, choices_made):
        options = "".join("{0}-{1}/".format(
                item[0], item[1]) for item in choices_made.items())
        return reverse("lizard_fancylayers.homepage", args=(options,))

    def dispatch(self, request, choices, *args):
        self.choices_made = self.make_choices_made(choices)
        return super(HomepageView, self).dispatch(request)

    def make_choices_made(self, choices):
        choicelist = choices.split('/')[:-1]

        choicedict = {}
        for choice in choicelist:
            identifier, value = choice.split('-')
            choicedict[identifier] = value

        return datasource.ChoicesMade(dict=choicedict)

    @property
    def datasource(self):
        if not hasattr(self, '_datasource'):
            self._datasource = datasource.datasource(self.choices_made)
        return self._datasource

    def visible_criteria(self):
        try:
            datasource = self.datasource
            if datasource is None:
                return []
            criteria = datasource.visible_criteria()
            for crit in criteria:
                criterion = crit['criterion']
                options = crit['options']

                for option in options.iter_options():
                    # Suppose we chose this value
                    new_choices_made = self.choices_made.add(
                        criterion.identifier,
                        option.identifier)
                    # Could we draw it on the map then?
                    if datasource.is_drawable(new_choices_made):
                        # Make it a workspace-acceptable
                        option.workspace_acceptable = WorkspaceAcceptable(
                            name=option.description,
                            adapter_name='adapter_fancylayers',
                            adapter_layer_json=simplejson.dumps({
                                    'choices_made': new_choices_made.json()}))
                    else:
                        # Give it a URL that makes it choosable
                        option.url = self.make_url(new_choices_made)

            return criteria
        except Exception, e:
            logger.warn("Caught exception in visible_criteria: {0}".
                        format(e))

    def forgettable_criteria(self):
        forgettable_criteria = []
        datasource = self.datasource
        if datasource is None:
            return []
        for criterion in self.datasource.criteria():
            if criterion.identifier not in self.choices_made:
                continue
            forgettable_criteria.append({
                    'identifier': criterion.identifier,
                    'description': criterion.description,
                    'url': self.make_url(
                        self.choices_made.forget(criterion.identifier)),
                    'value': self.choices_made[criterion.identifier]
                    })

        return forgettable_criteria
