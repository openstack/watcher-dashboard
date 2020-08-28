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

import json
import logging

from django.urls import reverse_lazy
from django.utils.translation import ugettext_lazy as _
import horizon.exceptions
from horizon import forms
import horizon.tables
import horizon.tabs
import horizon.workflows

from watcher_dashboard.api import watcher
from watcher_dashboard.content.audit_templates import forms as wforms
from watcher_dashboard.content.audit_templates import tables
from watcher_dashboard.content.audit_templates import tabs as wtabs

LOG = logging.getLogger(__name__)


class IndexView(horizon.tables.DataTableView):
    table_class = tables.AuditTemplatesTable
    template_name = 'infra_optim/audit_templates/index.html'
    page_title = _("Audit Templates")

    def get_context_data(self, **kwargs):
        context = super(IndexView, self).get_context_data(**kwargs)
        context['audit_templates_count'] = self.get_count()
        return context

    def get_data(self):
        audit_templates = []
        search_opts = self.get_filters()
        try:
            audit_templates = watcher.AuditTemplate.list(
                self.request, **search_opts)
        except Exception as exc:
            LOG.exception(exc)
            horizon.exceptions.handle(
                self.request,
                _("Unable to retrieve audit template information."))
        return audit_templates

    def get_count(self):
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


class CreateView(forms.ModalFormView):
    form_class = wforms.CreateForm
    form_id = "create_audit_templates_form"
    modal_header = _("Create Audit Template")
    template_name = 'infra_optim/audit_templates/create.html'
    success_url = reverse_lazy("horizon:admin:audit_templates:index")
    page_title = _("Create an Audit Template")
    submit_label = _("Create Audit Template")
    submit_url = reverse_lazy("horizon:admin:audit_templates:create")

    def get_object_id(self, obj):
        return obj.uuid


class DetailView(horizon.tabs.TabbedTableView):
    tab_group_class = wtabs.AuditTemplateDetailTabs
    template_name = 'infra_optim/audit_templates/details.html'
    redirect_url = 'horizon:admin:audit_templates:index'
    page_title = _("Audit Template Details: {{ audit_template.name }}")

    def _get_data(self):
        audit_template_uuid = None
        try:
            LOG.info(self.kwargs)
            audit_template_uuid = self.kwargs['audit_template_uuid']
            audit_template = watcher.AuditTemplate.get(
                self.request, audit_template_uuid)
            if audit_template.scope:
                audit_template.scope = json.dumps(audit_template.scope)

        except Exception as exc:
            LOG.exception(exc)
            msg = _('Unable to retrieve details for audit template "%s".') \
                % audit_template_uuid
            horizon.exceptions.handle(
                self.request, msg,
                redirect=self.redirect_url)
        return audit_template

    def get_related_audits_data(self):
        try:
            audit_template = self._get_data()
            audits = watcher.Audit.list(
                self.request, audit_template=audit_template.uuid)
        except Exception as exc:
            LOG.exception(exc)
            audits = []
            msg = _('Audits list cannot be retrieved.')
            horizon.exceptions.handle(self.request, msg)
        return audits

    def get_context_data(self, **kwargs):
        context = super(DetailView, self).get_context_data(**kwargs)
        audit_template = self._get_data()
        context["audit_template"] = audit_template
        return context

    def get_tabs(self, request, *args, **kwargs):
        audit_template = self._get_data()
        # ports = self._get_ports()
        return self.tab_group_class(
            request, audit_template=audit_template, **kwargs)
