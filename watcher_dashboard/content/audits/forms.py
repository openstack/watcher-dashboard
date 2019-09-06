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
Forms for starting Watcher Audits.
"""
import logging

from django.urls import reverse
from django.utils.translation import ugettext_lazy as _

from horizon import exceptions
from horizon import forms
from horizon import messages

from watcher_dashboard.api import watcher

LOG = logging.getLogger(__name__)
ADD_AUDIT_TEMPLATES_URL = "horizon:admin:audit_templates:create"


class CreateForm(forms.SelfHandlingForm):
    audit_template = forms.DynamicChoiceField(
        label=_("Audit Template"),
        add_item_link=ADD_AUDIT_TEMPLATES_URL)
    audit_name = forms.CharField(max_length=255, label=_("Name"),
                                 help_text=_("An audit name should not "
                                 "duplicate with existed audits' names."),
                                 required=False)
    audit_type = forms.ChoiceField(label=_("Audit Type"),
                                   choices=[(None, _("Select Audit Type")),
                                            ('oneshot', _('ONESHOT')),
                                            ('continuous', _('CONTINUOUS'))],
                                   widget=forms.Select(attrs={
                                       'class': 'switchable',
                                       'data-slug': 'audit_type'
                                   }))
    interval = forms.CharField(label=_("Interval (in seconds or cron format)"),
                               help_text=_("Interval in seconds or cron"
                                           "format for CONTINUOUS audit"),
                               widget=forms.TextInput(attrs={
                                   'class': 'switched',
                                   'data-switch-on': 'audit_type',
                                   'data-audit_type-continuous':
                                   _("Interval (in seconds or cron"
                                     " format)")}),
                               required=False)
    failure_url = 'horizon:admin:audits:index'
    auto_trigger = forms.BooleanField(label=_("Auto Trigger"),
                                      required=False)

    def __init__(self, request, *args, **kwargs):
        super(CreateForm, self).__init__(request, *args, **kwargs)
        audit_templates = self._get_audit_template_list(request)
        self.fields['audit_template'].choices = audit_templates

    def _get_audit_template_list(self, request):
        try:
            audit_templates = watcher.AuditTemplate.list(self.request)
        except Exception as e:
            msg = _('Failed to get audit template list: %s') % str(e)
            LOG.info(msg)
            messages.warning(request, msg)
            audit_templates = []

        choices = [
            (audit_template.uuid, audit_template.name or audit_template.uuid)
            for audit_template in audit_templates
        ]

        if choices:
            choices.insert(0, ("", _("Select Audit Template")))
        else:
            choices.insert(0, ("", _("No Audit Template found")))
        return choices

    def clean(self):
        cleaned_data = super(CreateForm, self).clean()
        audit_type = cleaned_data.get('audit_type')
        if audit_type == 'continuous' and not cleaned_data.get('interval'):
            msg = _('Please input an interval for continuous audit')
            raise forms.ValidationError(msg)
        return cleaned_data

    def handle(self, request, data):
        try:
            params = {'audit_template_uuid': data.get('audit_template')}
            params['audit_type'] = data['audit_type'].upper()
            params['auto_trigger'] = data['auto_trigger']
            params['name'] = data['audit_name']
            if data['audit_type'] == 'continuous':
                params['interval'] = data['interval']
            else:
                params['interval'] = None
            audit = watcher.Audit.create(request, **params)
            message = _('Audit was successfully created.')
            messages.success(request, message)
            return audit
        except Exception as exc:
            if getattr(exc, 'http_status', None) == 409:
                msg = _('Error: Audit name already exists.')
            else:
                msg = _('Failed to create audit.')
            LOG.info(exc)
            redirect = reverse(self.failure_url)
            exceptions.handle(request, msg, redirect=redirect)
            return False
