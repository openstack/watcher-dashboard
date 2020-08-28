# Copyright (c) 2016 b<>com
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
# http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or
# implied.
# See the License for the specific language governing permissions and
# limitations under the License.

import logging

from django.utils.translation import ugettext_lazy as _
import horizon.exceptions
import horizon.tables
import horizon.tabs
from horizon.utils import memoized
import horizon.workflows

from watcher_dashboard.api import watcher
from watcher_dashboard.content.goals import tables
from watcher_dashboard.content.goals import tabs as wtabs
from watcher_dashboard.content.strategies import tables as strategies_tables

LOG = logging.getLogger(__name__)


class IndexView(horizon.tables.DataTableView):
    table_class = tables.GoalsTable
    template_name = 'infra_optim/goals/index.html'
    page_title = _("Goals")

    def get_context_data(self, **kwargs):
        context = super(IndexView, self).get_context_data(**kwargs)
        context['goals_count'] = self.get_goals_count()
        return context

    def get_data(self):
        goals = []
        search_opts = self.get_filters()
        try:
            goals = watcher.Goal.list(self.request, **search_opts)
        except Exception:
            horizon.exceptions.handle(
                self.request,
                _("Unable to retrieve goal information."))
        return goals

    def get_goals_count(self):
        return len(self.get_data())

    def get_filters(self):
        filters = {}
        filter_action = self.table._meta._filter_action
        if filter_action:
            filter_field = self.table.get_filter_field()
            if filter_action.is_api_filter(filter_field):
                filter_string = self.table.get_filter_string()
                if filter_field and filter_string:
                    filters[filter_field] = filter_string
        return filters


class DetailView(horizon.tables.MultiTableView):
    table_classes = (tables.EfficacySpecificationTable,
                     strategies_tables.RelatedStrategiesTable)

    tab_group_class = wtabs.GoalDetailTabs
    template_name = 'infra_optim/goals/details.html'
    redirect_url = 'horizon:admin:goals:index'
    page_title = _("Goal Details: {{ goal.name }}")

    @memoized.memoized_method
    def _get_data(self):
        goal_uuid = None
        try:
            goal_uuid = self.kwargs['goal_uuid']
            goal = watcher.Goal.get(self.request, goal_uuid)
        except Exception as exc:
            LOG.exception(exc)
            msg = _('Unable to retrieve details for goal "%s".') \
                % goal_uuid
            horizon.exceptions.handle(
                self.request, msg,
                redirect=self.redirect_url)
        return goal

    def get_related_strategies_data(self):
        try:
            goal = self._get_data()
            strategies = watcher.Strategy.list(self.request, goal=goal.uuid)
        except Exception as exc:
            LOG.exception(exc)
            strategies = []
            msg = _('Strategy list cannot be retrieved.')
            horizon.exceptions.handle(self.request, msg)

        return strategies

    def get_efficacy_specification_data(self):
        try:
            goal = self._get_data()
            indicators_spec = [watcher.EfficacyIndicatorSpec(spec)
                               for spec in goal.efficacy_specification]
        except Exception as exc:
            LOG.exception(exc)
            indicators_spec = []
            msg = _('Efficacy specification cannot be retrieved.')
            horizon.exceptions.handle(self.request, msg)

        return indicators_spec

    def get_context_data(self, **kwargs):
        context = super(DetailView, self).get_context_data(**kwargs)
        goal = self._get_data()
        context["goal"] = goal
        return context

    def get_tabs(self, request, *args, **kwargs):
        goal = self._get_data()
        # ports = self._get_ports()
        return self.tab_group_class(request, goal=goal,
                                    # ports=ports,
                                    **kwargs)
