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

from django.http import JsonResponse
from django.urls import reverse
from django.urls import reverse_lazy
from django.utils.safestring import mark_safe
from django.utils.translation import gettext_lazy as _
import horizon.exceptions
from horizon import forms
import horizon.tables
import horizon.tabs
from horizon.utils import memoized
import horizon.workflows
import yaml

from watcher_dashboard.api import watcher
from watcher_dashboard.content.action_plans import tables as action_plan_tables
from watcher_dashboard.content.audits import forms as wforms
from watcher_dashboard.content.audits import tables
from watcher_dashboard.content.audits import tabs as wtabs

LOG = logging.getLogger(__name__)


class IndexView(horizon.tables.DataTableView):
    table_class = tables.AuditsTable
    template_name = 'infra_optim/audits/index.html'
    page_title = _("Audits")

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        create_action = {
            'name': _("New Audit"),
            'url': reverse('horizon:admin:audits:create'),
            'icon': 'fa-plus',
            'ajax_modal': True,
        }
        context['header_actions'] = [create_action]
        context['audits_count'] = self.get_audits_count()
        return context

    def get_data(self):
        audits = []
        search_opts = self.get_filters()
        try:
            audits = watcher.Audit.list(self.request, **search_opts)
        except Exception:
            horizon.exceptions.handle(
                self.request,
                _("Unable to retrieve audit information."))
        return audits

    def get_audits_count(self):
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
    form_id = "create_audit_form"
    modal_header = _("Create Audit")
    template_name = 'infra_optim/audits/create.html'
    success_url = reverse_lazy("horizon:admin:audits:index")
    page_title = _("Create Audit")
    submit_label = _("Create Audit")
    submit_url = reverse_lazy("horizon:admin:audits:create")


class DetailView(horizon.tables.MultiTableView):
    table_classes = (action_plan_tables.RelatedActionPlansTable,)
    tab_group_class = wtabs.AuditDetailTabs
    template_name = 'infra_optim/audits/details.html'
    redirect_url = 'horizon:admin:audits:index'
    page_title = _("Audit Details: {{ audit.uuid }}")

    @memoized.memoized_method
    def _get_data(self):
        audit_uuid = None
        try:
            audit_uuid = self.kwargs['audit_uuid']
            audit = watcher.Audit.get(self.request, audit_uuid)
        except Exception:
            msg = _('Unable to retrieve details for audit "%s".') \
                % audit_uuid
            horizon.exceptions.handle(
                self.request, msg,
                redirect=self.redirect_url)
        return audit

    def _render_pretty_parameters(self, params):
        """Return a human-friendly rendering of parameters.

        It is used to render parameters on the audit details page
        in a YAML format for readability.

        Rules:
        - If params is a JSON string, parse it first.
        - If result is a dict/list, pretty-print as YAML in a <pre> block.
        - If result is a scalar (str/int/bool), return it as-is.
        - On any error, fall back to the original params value.
        """
        try:
            obj = params
            # Parameters may be stored as a JSON-serialized string. Try to
            # decode it but tolerate non-JSON strings (e.g. plain text).
            if isinstance(params, str):
                try:
                    obj = json.loads(params)
                except Exception:
                    obj = params

            # Dicts/lists are presented as indented YAML for readability.
            if isinstance(obj, dict | list):
                dumped = yaml.safe_dump(
                    obj,
                    default_flow_style=False,
                    sort_keys=False,
                )
                return mark_safe(  # noqa: S308  # nosec B703,B308
                    f'<pre style="margin:0">{dumped}</pre>'
                )

            # Scalars or unknown types: return directly.
            if obj is not None:
                return obj
        except Exception:
            # Any unexpected issue: show the raw parameters.
            return params

    def get_related_action_plans_data(self):
        try:
            action_plan = self._get_data()
            audits = watcher.ActionPlan.list(self.request,
                                             audit=action_plan.uuid)
        except Exception as exc:
            LOG.exception(exc)
            audits = []
            msg = _('Action plan list cannot be retrieved.')
            horizon.exceptions.handle(self.request, msg)
        return audits

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        audit = self._get_data()
        context["audit"] = audit
        # Prepare pretty parameters rendering (YAML) for the template. The
        # helper encapsulates the logic so it is easier to test/maintain.
        context["audit_parameters_pretty"] = self._render_pretty_parameters(
            getattr(audit, 'parameters', None)
        )
        return context

    def get_tabs(self, request, *args, **kwargs):
        audit = self._get_data()
        # ports = self._get_ports()
        return self.tab_group_class(request, audit=audit, **kwargs)


def get_strategy_parameters(request):
    """AJAX endpoint to get strategy parameters based on audit template."""
    try:
        audit_template_uuid = request.GET.get('audit_template_uuid')
        if not audit_template_uuid:
            return JsonResponse(
                {'error': 'Audit template UUID is required'},
                status=400)

        # Get the audit template
        audit_template = watcher.AuditTemplate.get(
            request, audit_template_uuid)

        if not audit_template.strategy_uuid:
            return JsonResponse({
                'strategy_name': audit_template.strategy_name or 'auto',
                'parameters_spec': {},
                'message': ('No specific strategy selected. Parameters will '
                            'be automatically determined.')
            })

        # Get the strategy details
        strategy = watcher.Strategy.get(request, audit_template.strategy_uuid)

        # Parse parameters_spec if it exists
        parameters_spec = {}
        if hasattr(strategy, 'parameters_spec') and strategy.parameters_spec:
            if isinstance(strategy.parameters_spec, dict):
                properties = strategy.parameters_spec.get('properties', {})
                parameters_spec = properties
            elif isinstance(strategy.parameters_spec, str):
                try:
                    parsed_spec = json.loads(strategy.parameters_spec)
                    parameters_spec = parsed_spec.get('properties', {})
                except ValueError:
                    parameters_spec = {}

        return JsonResponse({
            'strategy_name': strategy.display_name or strategy.name,
            'strategy_uuid': strategy.uuid,
            'parameters_spec': parameters_spec
        })

    except Exception as e:
        LOG.exception("Error getting strategy parameters")
        return JsonResponse({'error': str(e)}, status=500)
