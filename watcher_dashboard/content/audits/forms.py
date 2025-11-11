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
import json
import logging

from django.urls import reverse
from django.utils.translation import gettext_lazy as _

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
    parameters = forms.CharField(
        label=_("Strategy Parameters (JSON)"),
        help_text=_("Provide strategy parameters as a JSON object. "
                    "See examples on the right."),
        widget=forms.widgets.Textarea(attrs={
            'rows': 8,
            'placeholder': ('{\n'
                            '  "memory_threshold": 0.8,\n'
                            '  "enable_migration": true,\n'
                            '  "compute_nodes": [\n'
                            '    {"src_node": "compute1", '
                            '"dst_node": "compute2"}\n'
                            '  ]\n'
                            '}')
        }),
        required=False
    )
    start_time = forms.DateTimeField(
        label=_("Start time"),
        help_text=_("Local time in ISO 8601 (e.g. 2025-01-02T18:30:00); "
                    "only used for CONTINUOUS audits. Watcher converts local "
                    "time to UTC."),
        widget=forms.DateTimeInput(
            format="%Y-%m-%dT%H:%M:%S",
            attrs={
                'class': 'switched',
                'data-switch-on': 'audit_type',
                'data-audit_type-continuous': _(
                    "Start time (ISO 8601, local)"
                ),
                'placeholder': 'YYYY-MM-DDTHH:MM:SS'
            }
        ),
        required=False,
        input_formats=[
            '%Y-%m-%dT%H:%M',
            '%Y-%m-%dT%H:%M:%S',
            '%Y-%m-%dT%H:%M:%S.%f',
        ])
    end_time = forms.DateTimeField(
        label=_("End time"),
        help_text=_("Local time in ISO 8601 (e.g. 2025-01-02T18:30:00); "
                    "only used for CONTINUOUS audits. Watcher converts local "
                    "time to UTC."),
        widget=forms.DateTimeInput(
            format="%Y-%m-%dT%H:%M:%S",
            attrs={
                'class': 'switched',
                'data-switch-on': 'audit_type',
                'data-audit_type-continuous': _("End time (ISO 8601, local)"),
                'placeholder': 'YYYY-MM-DDTHH:MM:SS'
            }
        ),
        required=False,
        input_formats=[
            '%Y-%m-%dT%H:%M',
            '%Y-%m-%dT%H:%M:%S',
            '%Y-%m-%dT%H:%M:%S.%f',
        ])
    failure_url = 'horizon:admin:audits:index'
    auto_trigger = forms.BooleanField(label=_("Auto Trigger"),
                                      required=False)

    def __init__(self, request, *args, **kwargs):
        super().__init__(request, *args, **kwargs)
        audit_templates = self._get_audit_template_list(request)
        self.fields['audit_template'].choices = audit_templates
        # Keep fields visible; API microversion is enforced per-call in backend

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

    def _parse_parameters(self, param_string):
        """Parse parameters JSON string into a dictionary

        :param param_string: String containing a JSON object
        :returns: Dictionary of parsed parameters
        """
        if not param_string or not param_string.strip():
            return {}

        try:
            parsed = json.loads(param_string)
        except ValueError as e:
            raise forms.ValidationError(
                _('Parameters must be valid JSON: %s') % str(e))

        if not isinstance(parsed, dict):
            raise forms.ValidationError(
                _('Parameters must be a JSON object'))

        return parsed

    def clean(self):
        cleaned_data = super().clean()
        audit_type = cleaned_data.get('audit_type')
        if audit_type == 'continuous' and not cleaned_data.get('interval'):
            msg = _('Please input an interval for continuous audit')
            raise forms.ValidationError(msg)
        if audit_type == 'continuous':
            start_time = cleaned_data.get('start_time')
            end_time = cleaned_data.get('end_time')
            if start_time and end_time and end_time <= start_time:
                raise forms.ValidationError(
                    _('End time must be later than start time'))
        # Validate parameters
        param_string = cleaned_data.get('parameters', '')
        try:
            parsed_params = self._parse_parameters(param_string)
            cleaned_data['parsed_parameters'] = parsed_params
        except forms.ValidationError:
            raise
        return cleaned_data

    def handle(self, request, data):
        try:
            params = {'audit_template_uuid': data.get('audit_template')}
            params['audit_type'] = data['audit_type'].upper()
            params['auto_trigger'] = data['auto_trigger']
            params['name'] = data['audit_name']
            if data['audit_type'] == 'continuous':
                params['interval'] = data['interval']
                # Convert datetimes to ISO 8601 for API (local time)
                if data.get('start_time'):
                    params['start_time'] = data['start_time'].isoformat(
                        timespec='seconds')
                if data.get('end_time'):
                    params['end_time'] = data['end_time'].isoformat(
                        timespec='seconds')
            else:
                params['interval'] = None

            # Add parsed parameters if they exist
            parsed_parameters = data.get('parsed_parameters')
            if parsed_parameters:
                params['parameters'] = parsed_parameters

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
