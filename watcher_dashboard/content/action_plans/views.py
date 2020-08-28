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
from horizon import forms
import horizon.tables
import horizon.tabs
from horizon.utils import memoized
import horizon.workflows

from watcher_dashboard.api import watcher
from watcher_dashboard.content.action_plans import tables
from watcher_dashboard.content.actions import tables as action_tables
from watcher_dashboard.content.audits import forms as wforms

LOG = logging.getLogger(__name__)


class IndexView(horizon.tables.DataTableView):
    table_class = tables.ActionPlansTable
    template_name = 'infra_optim/action_plans/index.html'
    page_title = _("Action Plans")

    def get_context_data(self, **kwargs):
        context = super(IndexView, self).get_context_data(**kwargs)
        context['action_plans_count'] = self.get_action_plans_count()
        return context

    def get_data(self):
        action_plans = []
        search_opts = self.get_filters()
        try:
            action_plans = watcher.ActionPlan.list(
                self.request, **search_opts)
        except Exception as exc:
            LOG.exception(exc)
            horizon.exceptions.handle(
                self.request,
                _("Unable to retrieve action_plan information."))
        return action_plans

    def get_action_plans_count(self):
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


class ArchiveView(forms.ModalFormView):
    form_class = wforms.CreateForm
    form_id = "create_audit_form"
    modal_header = _("Create Audit")
    template_name = 'infra_optim/audits/create.html'
    page_title = _("Create Audit")
    submit_label = _("Create Audit")


class DetailView(horizon.tables.MultiTableView):
    table_classes = (
        action_tables.RelatedActionsTable,
        tables.RelatedEfficacyIndicatorsTable)
    template_name = 'infra_optim/action_plans/details.html'
    page_title = _("Action Plan Details: {{ action_plan.uuid }}")

    @memoized.memoized_method
    def _get_data(self):
        action_plan_uuid = None
        try:
            action_plan_uuid = self.kwargs['action_plan_uuid']
            action_plan = watcher.ActionPlan.get(
                self.request, action_plan_uuid)
        except Exception as exc:
            LOG.exception(exc)
            msg = _('Unable to retrieve details for action_plan "%s".') \
                % action_plan_uuid
            horizon.exceptions.handle(
                self.request, msg,
                redirect=self.redirect_url)
        return action_plan

    def get_related_wactions_data(self):
        try:
            action_plan = self._get_data()
            actions = watcher.Action.list(self.request,
                                          action_plan=action_plan.uuid)
        except Exception as exc:
            LOG.exception(exc)
            actions = []
            msg = _('Action list can not be retrieved.')
            horizon.exceptions.handle(self.request, msg)
        return actions

    def get_related_efficacy_indicators_data(self):
        try:
            action_plan = self._get_data()
            efficacy_indicators = [
                watcher.EfficacyIndicator(indicator)
                for indicator in action_plan.efficacy_indicators]
        except Exception as exc:
            LOG.exception(exc)
            msg = _('Failed to get the efficacy indicators: %s') % str(exc)
            LOG.info(msg)
            horizon.messages.warning(self.request, msg)

        return efficacy_indicators

    def get_context_data(self, **kwargs):
        context = super(DetailView, self).get_context_data(**kwargs)
        action_plan = self._get_data()
        context["action_plan"] = action_plan
        LOG.info('*********************************')
        LOG.info(action_plan)
        LOG.info('*********************************')
        return context

    def get_tabs(self, request, *args, **kwargs):
        action_plan = self._get_data()
        return self.tab_group_class(
            request, action_plan=action_plan, **kwargs)
