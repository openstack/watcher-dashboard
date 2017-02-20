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

import collections

from django.utils.translation import ugettext_lazy as _
import horizon.exceptions
import horizon.tables
import horizon.tabs
from horizon.utils import memoized
import horizon.workflows

from watcher_dashboard.api import watcher
from watcher_dashboard.content.actions import tables
from watcher_dashboard.content.actions import tabs as wtabs


class IndexView(horizon.tables.DataTableView):
    table_class = tables.ActionsTable
    template_name = 'infra_optim/actions/index.html'
    page_title = _("Actions")

    def get_context_data(self, **kwargs):
        context = super(IndexView, self).get_context_data(**kwargs)
        context['audits_count'] = self.get_actions_count()
        return context

    def get_data(self):
        actions = []
        search_opts = self.get_filters()
        try:
            actions = watcher.Action.list(self.request, **search_opts)
        except Exception:
            horizon.exceptions.handle(
                self.request,
                _("Unable to retrieve action information."))
        return actions

    def get_actions_count(self):
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
    table_classes = [tables.ActionParametersTable]
    tab_group_class = wtabs.ActionDetailTabs
    template_name = 'infra_optim/actions/details.html'
    redirect_url = 'horizon:admin:actions:index'
    page_title = _("Action Details: {{ action.uuid }}")

    @memoized.memoized_method
    def _get_data(self):
        action_uuid = None
        try:
            action_uuid = self.kwargs['action_uuid']
            action = watcher.Action.get(self.request, action_uuid)
        except Exception:
            msg = _('Unable to retrieve details for action "%s".') \
                % action_uuid
            horizon.exceptions.handle(
                self.request, msg,
                redirect=self.redirect_url)
        return action

    def get_parameters_data(self):
        action = self._get_data()
        parameter_cls = collections.namedtuple(
            'Parameter', field_names=['name', 'value'])

        return [parameter_cls(name=name, value=value)
                for name, value in action.input_parameters.items()]

    def get_context_data(self, **kwargs):
        context = super(DetailView, self).get_context_data(**kwargs)
        action = self._get_data()
        context["action"] = action
        return context

    def get_tabs(self, request, *args, **kwargs):
        action = self._get_data()
        # ports = self._get_ports()
        return self.tab_group_class(request, action=action,
                                    # ports=ports,
                                    **kwargs)
