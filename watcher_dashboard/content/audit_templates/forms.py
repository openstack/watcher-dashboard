# Copyright 2012,  Nachi Ueno,  NTT MCL,  Inc.
# All rights reserved.

# Licensed under the Apache License, Version 2.0 (the "License"); you may
# not use this file except in compliance with the License. You may obtain
# a copy of the License at
#
#      http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS, WITHOUT
# WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the
# License for the specific language governing permissions and limitations
# under the License.

"""
Forms for starting Watcher Audit Templates.
"""
import logging

from django.core import exceptions as core_exc
from django.urls import reverse
from django.utils.translation import gettext_lazy as _
from horizon import exceptions
from horizon import forms
from horizon import messages
import yaml

from watcher_dashboard.api import watcher

LOG = logging.getLogger(__name__)


class YamlValidator:
    message = _('Enter a valid YAML or JSON value.')
    code = 'invalid'

    def __init__(self, message=None):
        if message:
            self.message = message

    def __call__(self, value):
        try:
            yaml.safe_load(value)
        except Exception:
            raise core_exc.ValidationError(self.message, code=self.code)


class CreateForm(forms.SelfHandlingForm):
    name = forms.CharField(max_length=255, label=_("Name"))
    description = forms.CharField(max_length=255, label=_("Description"),
                                  required=False)
    goal = forms.ChoiceField(label=_('Goal'))
    strategy = forms.DynamicChoiceField(label=_('Strategy'), required=False)

    scope = forms.CharField(
        label=_('Scope'), required=False,
        widget=forms.widgets.Textarea,
        validators=[YamlValidator()])

    failure_url = 'horizon:admin:audit_templates:index'

    def __init__(self, request, *args, **kwargs):
        super().__init__(request, *args, **kwargs)
        goals = self._get_goal_list(request)

        if goals:
            self.fields['goal'].choices = goals
        else:
            del self.fields['goal']

        # Defer strategy choices to be populated dynamically based on goal
        # selection via AJAX in the template. Start with only the default.
        if 'strategy' in self.fields:
            self.fields['strategy'].choices = [("", _("Select Strategy"))]

        # If this is a POST, populate strategies for the selected goal so that
        # server-side validation accepts the submitted value (mirrors the AJAX
        # behavior in the template for client-side population).
        selected_goal = (
            self.data.get('goal') if hasattr(self, 'data') else None
        )
        if selected_goal and 'strategy' in self.fields:
            filtered_strategies = self._get_strategy_list_for_goal(
                request, selected_goal)
            if filtered_strategies:
                self.fields['strategy'].choices = filtered_strategies

    def _get_goal_list(self, request):
        try:
            goals = watcher.Goal.list(self.request)
        except Exception as exc:
            msg = _('Failed to get goals list: %s') % str(exc)
            LOG.info(msg)
            messages.warning(request, msg)
            messages.warning(request, exc)
            goals = []

        choices = [
            (goal.uuid, goal.display_name)
            for goal in goals
        ]

        if choices:
            choices.insert(0, ("", _("Select Goal")))
        return choices

    def _get_strategy_list(self, request, goals):
        try:
            strategies = watcher.Strategy.list(self.request)
        except Exception as exc:
            msg = _('Failed to get the list of available strategies.')
            LOG.info(msg)
            messages.warning(request, msg)
            messages.warning(request, exc)
            strategies = []

        _goals = {}
        for goal in goals:
            _goals[goal[0]] = goal[1]

        choices = [
            (strategy.uuid, strategy.display_name +
             ' (GOAL: ' + _goals[strategy.goal_uuid] + ')')
            for strategy in strategies
        ]

        if choices:
            choices.insert(0, ("", _("Select Strategy")))
        return choices

    def _get_strategy_list_for_goal(self, request, goal_uuid):
        try:
            strategies = watcher.Strategy.list(self.request, goal=goal_uuid)
        except Exception as exc:
            msg = _('Failed to get strategies for selected goal.')
            LOG.info(msg)
            messages.warning(request, msg)
            messages.warning(request, exc)
            strategies = []

        choices = [
            (
                strategy.uuid,
                getattr(strategy, 'display_name', None) or
                getattr(strategy, 'name', '')
            )
            for strategy in strategies
        ]

        if choices:
            choices.insert(0, ("", _("Select Strategy")))
        return choices

    def handle(self, request, data):
        try:
            params = {'name': data['name']}
            params['description'] = data['description']
            params['goal'] = data['goal']
            params['strategy'] = data['strategy'] or None
            params['scope'] = [] if not data['scope'] else yaml.safe_load(
                data['scope'])
            audit_tpl = watcher.AuditTemplate.create(request, **params)
            message = _('Audit Template was successfully created.')
            messages.success(request, message)
            return audit_tpl
        except Exception as exc:
            msg = _('Failed to create audit template.')
            LOG.info(exc)
            redirect = reverse(self.failure_url)
            exceptions.handle(request, msg, redirect=redirect)
            return False
