#    Licensed under the Apache License, Version 2.0 (the "License"); you may
#    not use this file except in compliance with the License. You may obtain
#    a copy of the License at
#
#         http://www.apache.org/licenses/LICENSE-2.0
#
#    Unless required by applicable law or agreed to in writing, software
#    distributed under the License is distributed on an "AS IS" BASIS, WITHOUT
#    WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the
#    License for the specific language governing permissions and limitations
#    under the License.

from __future__ import unicode_literals

import logging

from django.conf import settings
from django.utils.translation import ugettext_lazy as _
from openstack_dashboard.api import base
from watcherclient import client as wc

from watcher_dashboard.utils import errors as errors_utils

LOG = logging.getLogger(__name__)
WATCHER_SERVICE = 'infra-optim'


def watcherclient(request, password=None):
    api_version = "1"
    insecure = getattr(settings, 'OPENSTACK_SSL_NO_VERIFY', False)
    ca_file = getattr(settings, 'OPENSTACK_SSL_CACERT', None)
    endpoint = base.url_for(request, WATCHER_SERVICE)

    LOG.debug('watcherclient connection created using token "%s" and url "%s"'
              % (request.user.token.id, endpoint))

    client = wc.get_client(
        api_version,
        watcher_url=endpoint,
        insecure=insecure,
        ca_file=ca_file,
        username=request.user.username,
        password=password,
        os_auth_token=request.user.token.id
    )
    return client


class Audit(base.APIResourceWrapper):
    _attrs = ('uuid', 'created_at', 'modified_at', 'deleted_at',
              'deadline', 'state', 'type', 'audit_template_uuid',
              'audit_template_name')

    def __init__(self, apiresource, request=None):
        super(Audit, self).__init__(apiresource)
        self._request = request

    @classmethod
    def create(cls, request, audit_template_uuid, type, deadline):
        """Create an audit in Watcher

        :param request: request object
        :type  request: django.http.HttpRequest

        :param audit_template: audit audit_template
        :type  audit_template: string

        :param type: audit type
        :type  type: string

        :param deadline: audit deadline
        :type  deadline: string

        :return: the created Audit object
        :rtype:  watcher_dashboard.api.watcher.Audit
        """
        audit = watcherclient(request).audit.create(
            audit_template_uuid=audit_template_uuid, type=type,
            deadline=deadline)
        return cls(audit, request=request)

    @classmethod
    def list(cls, request, audit_template_filter):
        """Return a list of audits in Watcher

        :param request: request object
        :type  request: django.http.HttpRequest

        :param audit_template_filter: audit_template filter, name or uuid
        :type  audit_template_filter: string

        :return: list of audits, or an empty list if there are none
        :rtype:  list of watcher_dashboard.api.watcher.Audit
        """
        audits = watcherclient(request).audit.list(
            audit_template=audit_template_filter)
        return [cls(audit, request=request) for audit in audits]

    @classmethod
    @errors_utils.handle_errors(_("Unable to retrieve audit"))
    def get(cls, request, audit_id):
        """Return the audit that matches the ID

        :param request: request object
        :type  request: django.http.HttpRequest

        :param audit_id: id of audit to be retrieved
        :type  audit_id: int

        :return: matching audit, or None if no audit matches
                 the ID
        :rtype:  watcher_dashboard.api.watcher.Audit
        """
        audit = watcherclient(request).audit.get(audit_id=audit_id)
        return cls(audit, request=request)

    @classmethod
    def delete(cls, request, audit_id):
        """Delete an audit

        :param request: request object
        :type  request: django.http.HttpRequest

        :param audit_id: audit id
        :type  audit_id: int
        """
        watcherclient(request).audit.delete(audit_id=audit_id)

    @property
    def id(self):
        return self.uuid


class AuditTemplate(base.APIDictWrapper):
    _attrs = ('uuid', 'created_at', 'updated_at', 'deleted_at',
              'description', 'host_aggregate', 'name',
              'extra', 'goal')

    def __init__(self, apiresource, request=None):
        super(AuditTemplate, self).__init__(apiresource)
        self._request = request

    @classmethod
    def create(cls, request, name, goal, description, host_aggregate):
        """Create an audit template in Watcher

        :param request: request object
        :type  request: django.http.HttpRequest

        :param name: Name for this audit template
        :type  name: string

        :param goal: Goal Type associated to this audit template
        :type  goal: string

        :param description: Descrition of the audit template
        :type  description: string

        :param host_aggregate: Name or ID of the host aggregate targeted\
        by this audit template
        :type  host_aggregate: string

        :param audit_template: audit audit_template
        :type  audit_template: string

        :return: the created Audit Template object
        :rtype:  watcher_dashboard.api.watcher.AuditTemplate
        """
        audit_template = watcherclient(request).audit_template.create(
            name=name,
            goal=goal,
            description=description,
            host_aggregate=host_aggregate
            )

        return audit_template

    @classmethod
    def patch(cls, request, audit_template_id, parameters):
        """Update an audit in Watcher

        :param request: request object
        :type  request: django.http.HttpRequest

        :param audit_template_id: id of the audit template we want to update
        :type  audit_template_id: string

        :param parameters: new values for the audit template's parameters
        :type  parameters: dict

        :return: the updated Audit Template object
        :rtype:  watcher_dashboard.api.watcher.AuditTemplate
        """
        parameter_list = [{
            'name': str(name),
            'value': str(value),
        } for (name, value) in parameters.items()]
        audit_template = watcherclient(request).audit_template.patch(
            audit_template_id, parameter_list)
        return audit_template

    @classmethod
    def list(cls, request, filter):
        """Return a list of audit templates in Watcher

        :param request: request object
        :type  request: django.http.HttpRequest

        :param filter: audit template filter
        :type  filter: string

        :return: list of audit templates, or an empty list if there are none
        :rtype:  list of watcher_dashboard.api.watcher.AuditTemplate
        """

        audit_templates = watcherclient(request).audit_template.list(
            name=filter)
        return audit_templates

    @classmethod
    @errors_utils.handle_errors(_("Unable to retrieve audit template"))
    def get(cls, request, audit_template_id):
        """Return the audit template that matches the ID

        :param request: request object
        :type  request: django.http.HttpRequest

        :param audit_template_id: id of audit template to be retrieved
        :type  audit_template_id: int

        :return: matching audit template, or None if no audit template matches
                 the ID
        :rtype:  watcher_dashboard.api.watcher.AuditTemplate
        """
        audit_template = watcherclient(request).audit_template.get(
            audit_template_id=audit_template_id)
        # return cls(audit, request=request)
        return audit_template

    @classmethod
    @errors_utils.handle_errors(_("Unable to retrieve audit template goal"))
    def get_goals(cls, request):
        """Return the audit template goal that matches the ID

        :param request: request object
        :type  request: django.http.HttpRequest

        :param audit_template_id: id of audit template to be retrieved
        :type  audit_template_id: int

        :return: matching audit template, or None if no audit template matches
                 the ID
        :rtype:  watcher_dashboard.api.watcher.AuditTemplate
        """

        goals = watcherclient(request).goal.list()
        return map(lambda goal: goal.name, goals)

    @classmethod
    def delete(cls, request, audit_template_id):
        """Delete an audit_template

        :param request: request object
        :type  request: django.http.HttpRequest

        :param audit_template_id: audit id
        :type  audit_template_id: int
        """
        watcherclient(request).audit_template.delete(
            audit_template_id=audit_template_id)

    @property
    def id(self):
        return self.uuid


class ActionPlan(base.APIResourceWrapper):
    _attrs = ('uuid', 'created_at', 'updated_at', 'deleted_at',
              'audit_uuid', 'state')

    def __init__(self, apiresource, request=None):
        super(ActionPlan, self).__init__(apiresource)
        self._request = request

    @classmethod
    def list(cls, request, audit_filter):
        """Return a list of action plans in Watcher

        :param request: request object
        :type  request: django.http.HttpRequest

        :param audit_filter: audit id filter
        :type  audit_filter: string

        :return: list of action plans, or an empty list if there are none
        :rtype:  list of watcher_dashboard.api.watcher.ActionPlan
        """
        action_plans = watcherclient(request).action_plan.list(
            audit=audit_filter)
        return [cls(action_plan, request=request)
                for action_plan in action_plans]

    @classmethod
    @errors_utils.handle_errors(_("Unable to retrieve action plan"))
    def get(cls, request, action_plan_id):
        """Return the action plan that matches the ID

        :param request: request object
        :type  request: django.http.HttpRequest

        :param action_plan_id: id of action plan to be retrieved
        :type  action_plan_id: int

        :return: matching action plan, or None if no action plan matches
                 the ID
        :rtype:  watcher_dashboard.api.watcher.ActionPlan
        """
        action_plan = watcherclient(request).action_plan.get(
            action_plan_id=action_plan_id)
        return cls(action_plan, request=request)

    @classmethod
    def delete(cls, request, action_plan_id):
        """Delete an action plan

        :param request: request object
        :type  request: django.http.HttpRequest

        :param action_plan_id: audit id
        :type  action_plan_id: int
        """
        watcherclient(request).action_plan.delete(
            action_plan_id=action_plan_id)

    @classmethod
    def start(cls, request, action_plan_id):
        """Start an Action Plan

        :param request: request object
        :type  request: django.http.HttpRequest

        :param action_plan_id: audit id
        :type  action_plan_id: int
        """
        patch = []
        patch.append({'op': 'replace', 'path': '/state', 'value': 'PENDING'})
        watcherclient(request).action_plan.update(action_plan_id, patch)

    @property
    def id(self):
        return self.uuid


class Action(base.APIResourceWrapper):
    _attrs = ('uuid', 'created_at', 'updated_at', 'deleted_at', 'next_uuid',
              'description', 'alarm', 'state', 'action_plan_uuid',
              'action_type', 'applies_to', 'src', 'dst', 'parameter')

    def __init__(self, apiresource, request=None):
        super(Action, self).__init__(apiresource)
        self._request = request

    @classmethod
    def list(cls, request, action_plan_filter):
        """Return a list of actions in Watcher

        :param request: request object
        :type  request: django.http.HttpRequest

        :param action_plan_filter: action_plan id filter
        :type  action_plan_filter: string

        :return: list of actions, or an empty list if there are none
        :rtype:  list of watcher_dashboard.api.watcher.Action
        """

        actions = watcherclient(request).action.list(
            action_plan=action_plan_filter, detail=True)
        return [cls(action, request=request)
                for action in actions]

    @classmethod
    @errors_utils.handle_errors(_("Unable to retrieve action"))
    def get(cls, request, action_id):
        """Return the action that matches the ID

        :param request: request object
        :type  request: django.http.HttpRequest

        :param action_id: id of action to be retrieved
        :type  action_id: int

        :return: matching action, or None if no action matches
                 the ID
        :rtype:  watcher_dashboard.api.watcher.Action
        """
        action = watcherclient(request).action.get(
            action_id=action_id)
        return cls(action, request=request)

    @classmethod
    def delete(cls, request, action_id):
        """Delete an action

        :param request: request object
        :type  request: django.http.HttpRequest

        :param action_id: action_plan id
        :type  action_id: int
        """
        watcherclient(request).action.delete(
            action_id=action_id)

    @classmethod
    def start(cls, request, action_id):
        """Start an Action Plan

        :param request: request object
        :type  request: django.http.HttpRequest

        :param action_id: action_plan id
        :type  action_id: int
        """
        patch = []
        patch.append({'op': 'replace', 'path': '/state', 'value': 'PENDING'})
        watcherclient(request).action.update(action_id, patch)

    @property
    def id(self):
        return self.uuid
