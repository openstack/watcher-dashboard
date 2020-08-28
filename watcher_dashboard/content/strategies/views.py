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
from watcher_dashboard.content.strategies import tables
from watcher_dashboard.content.strategies import tabs as wtabs

LOG = logging.getLogger(__name__)


class IndexView(horizon.tables.DataTableView):
    table_class = tables.StrategiesTable
    template_name = 'infra_optim/strategies/index.html'
    page_title = _("Strategies")

    def get_context_data(self, **kwargs):
        context = super(IndexView, self).get_context_data(**kwargs)
        context['strategies_count'] = self.get_strategies_count()
        return context

    def get_data(self):
        strategies = []
        search_opts = self.get_filters()
        try:
            strategies = watcher.Strategy.list(self.request, **search_opts)
        except Exception as exc:
            LOG.exception(exc)
            horizon.exceptions.handle(
                self.request,
                _("Unable to retrieve strategy information."))
        return strategies

    def get_strategies_count(self):
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


class DetailView(horizon.tabs.TabbedTableView):
    tab_group_class = wtabs.StrategyDetailTabs
    template_name = 'infra_optim/strategies/details.html'
    redirect_url = 'horizon:admin:strategies:index'
    page_title = _("Strategy Details: {{ strategy.name }}")

    @memoized.memoized_method
    def _get_data(self):
        strategy_uuid = None
        try:
            strategy_uuid = self.kwargs['strategy_uuid']
            strategy = watcher.Strategy.get(self.request, strategy_uuid)
        except Exception as exc:
            LOG.exception(exc)
            msg = _('Unable to retrieve details for strategy "%s".') \
                % strategy_uuid
            horizon.exceptions.handle(
                self.request, msg,
                redirect=self.redirect_url)
        return strategy

    def get_context_data(self, **kwargs):
        context = super(DetailView, self).get_context_data(**kwargs)
        strategy = self._get_data()
        context["strategy"] = strategy
        return context

    def get_tabs(self, request, *args, **kwargs):
        strategy = self._get_data()
        return self.tab_group_class(request, strategy=strategy, **kwargs)
