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

from django.core.urlresolvers import reverse
from django.utils.translation import ugettext_lazy as _

from horizon import exceptions
from horizon import forms
from horizon import messages

from watcher_dashboard.api import watcher

LOG = logging.getLogger(__name__)


class CreateForm(forms.SelfHandlingForm):
    name = forms.CharField(max_length=255, label=_("Name"))
    description = forms.CharField(max_length=255, label=_("Description"),
                                  required=False)
    goal = forms.ChoiceField(label=_('Goal'),
                             required=True,
                             )

    failure_url = 'horizon:admin:audit_templates:index'

    def __init__(self, request, *args, **kwargs):
        super(CreateForm, self).__init__(request, *args, **kwargs)
        goals = self._get_goal_list(request)
        if goals:
            self.fields['goal'].choices = goals
        else:
            del self.fields['goal']

    def _get_goal_list(self, request):
        try:
            goals = watcher.AuditTemplate.get_goals(self.request)
        except Exception as exc:
            msg = _('Failed to get goals list.')
            LOG.info(msg)
            messages.warning(request, msg)
            messages.warning(request, exc)
            goals = []

        choices = [
            (goal, goal)
            for goal in goals
        ]

        if choices:
            choices.insert(0, ("", _("Select Goal")))
        return choices

    def handle(self, request, data):
        try:
            params = {'name': data['name']}
            params['goal'] = data['goal']
            params['description'] = data['description']
            params['host_aggregate'] = None
            audit_temp = watcher.AuditTemplate.create(request, **params)
            message = _('Audit Template was successfully created.')
            messages.success(request, message)
            return audit_temp
        except Exception as exc:
            msg = _('Failed to create audit template"%s".') % data['name']
            LOG.info(exc)
            redirect = reverse(self.failure_url)
            exceptions.handle(request, msg, redirect=redirect)
            return False
