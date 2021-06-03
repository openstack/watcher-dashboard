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
    insert_watcher_policy_file()

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


def insert_watcher_policy_file():
    policy_files = getattr(settings, 'POLICY_FILES', {})
    policy_files['infra-optim'] = 'watcher_policy.json'
    setattr(settings, 'POLICY_FILES', policy_files)


class Audit(base.APIDictWrapper):
    _attrs = ('uuid', 'name', 'created_at', 'modified_at', 'deleted_at',
              'state', 'audit_type', 'audit_template_uuid',
              'audit_template_name', 'interval')

    def __init__(self, apiresource, request=None):
        super(Audit, self).__init__(apiresource)
        self._request = request

    @classmethod
    def create(cls, request, audit_template_uuid, audit_type, name=None,
               auto_trigger=False, interval=None):

        """Create an audit in Watcher

        :param request: request object
        :type  request: django.http.HttpRequest

        :param audit_template_uuid: related audit template UUID
        :type  audit_template_uuid: string

        :param audit_type: audit type
        :type  audit_type: string

        :param interval: Audit interval (default: None)
        :type  interval: int

        :param name: Name for this audit
        :type  name: string

        :return: the created Audit object
        :rtype:  :py:class:`~.Audit`
        """

        if interval:
            return watcherclient(request).audit.create(
                audit_template_uuid=audit_template_uuid, audit_type=audit_type,
                auto_trigger=auto_trigger, interval=interval, name=name)
        else:
            return watcherclient(request).audit.create(
                audit_template_uuid=audit_template_uuid, audit_type=audit_type,
                auto_trigger=auto_trigger, name=name)

    @classmethod
    def list(cls, request, **filters):
        """Return a list of audits in Watcher

        :param request: request object
        :type  request: django.http.HttpRequest

        :param filters: key/value kwargs used as filters
        :type  filters: dict

        :return: list of audits, or an empty list if there are none
        :rtype:  list of :py:class:`~.Audit`
        """
        return watcherclient(request).audit.list(detail=True, **filters)

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
        :rtype:  :py:class:`~.Audit`
        """
        return watcherclient(request).audit.get(audit=audit_id)

    @classmethod
    def delete(cls, request, audit_id):
        """Delete an audit

        :param request: request object
        :type  request: django.http.HttpRequest

        :param audit_id: audit id
        :type  audit_id: int
        """
        return watcherclient(request).audit.delete(audit=audit_id)

    @property
    def id(self):
        return self.uuid


class AuditTemplate(base.APIDictWrapper):
    _attrs = ('uuid', 'description', 'scope', 'name', 'goal_uuid', 'goal_name',
              'strategy_uuid', 'strategy_name', 'created_at', 'updated_at',
              'deleted_at')

    def __init__(self, apiresource, request=None):
        super(AuditTemplate, self).__init__(apiresource)
        self._request = request

    @classmethod
    def create(cls, request, name, goal, strategy,
               description, scope):
        """Create an audit template in Watcher

        :param request: request object
        :type  request: django.http.HttpRequest

        :param name: Name for this audit template
        :type  name: string

        :param goal: Goal UUID or name associated to this audit template
        :type  goal: string

        :param strategy: Strategy UUID or name associated to this audit
                         template
        :type  strategy: string

        :param description: Descrition of the audit template
        :type  description: string

        :param scope: Audit scope
        :type  scope: list of list of dict

        :param audit_template: audit template
        :type  audit_template: string

        :return: the created Audit Template object
        :rtype:  :py:class:`~.AuditTemplate`
        """
        audit_template = watcherclient(request).audit_template.create(
            name=name,
            goal=goal,
            strategy=strategy,
            description=description,
            scope=scope,
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
        :rtype:  :py:class:`~.AuditTemplate`
        """
        parameter_list = [{
            'name': str(name),
            'value': str(value),
        } for (name, value) in parameters.items()]
        audit_template = watcherclient(request).audit_template.patch(
            audit_template_id, parameter_list)
        return audit_template

    @classmethod
    def list(cls, request, **filters):
        """Return a list of audit templates in Watcher

        :param request: request object
        :type  request: django.http.HttpRequest

        :param filters: key/value kwargs used as filters
        :type  filters: dict

        :return: list of audit templates, or an empty list if there are none
        :rtype:  list of :py:class:`~.AuditTemplate`
        """
        return watcherclient(request).audit_template.list(
            detail=True, **filters)

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
        :rtype:  :py:class:`~.AuditTemplate`
        """
        return watcherclient(request).audit_template.get(
            audit_template_id=audit_template_id)

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


class ActionPlan(base.APIDictWrapper):
    _attrs = ('uuid', 'created_at', 'updated_at', 'deleted_at',
              'audit_uuid', 'state')

    def __init__(self, apiresource, request=None):
        super(ActionPlan, self).__init__(apiresource)
        self._request = request

    @classmethod
    def list(cls, request, **filters):
        """Return a list of action plans in Watcher

        :param request: request object
        :type  request: django.http.HttpRequest

        :param filters: key/value kwargs used as filters
        :type  filters: dict

        :return: list of action plans, or an empty list if there are none
        :rtype:  list of :py:class:`~.ActionPlan`
        """
        return watcherclient(request).action_plan.list(detail=True, **filters)

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
        :rtype:  :py:class:`~.ActionPlan`
        """
        return watcherclient(request).action_plan.get(
            action_plan_id=action_plan_id)

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
        watcherclient(request).action_plan.start(action_plan_id)

    @property
    def id(self):
        return self.uuid


class Action(base.APIDictWrapper):
    _attrs = ('uuid', 'created_at', 'updated_at', 'deleted_at', 'next_uuid',
              'description', 'state', 'action_plan_uuid',
              'action_type', 'applies_to', 'src', 'dst', 'parameter')

    def __init__(self, apiresource, request=None):
        super(Action, self).__init__(apiresource)
        self._request = request

    @classmethod
    def list(cls, request, **filters):
        """Return a list of actions in Watcher

        :param request: request object
        :type  request: django.http.HttpRequest

        :param filters: key/value kwargs used as filters
        :type  filters: dict

        :return: list of actions, or an empty list if there are none
        :rtype:  list of :py:class:`~.Action`
        """
        return watcherclient(request).action.list(detail=True, **filters)

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
        :rtype:  :py:class:`~.Action`
        """
        return watcherclient(request).action.get(action_id=action_id)

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


class Goal(base.APIDictWrapper):
    """Goal resource."""

    _attrs = ('uuid', 'name', 'display_name', 'created_at',
              'updated_at', 'deleted_at', 'efficacy_specifications')

    def __init__(self, apiresource, request=None):
        super(Goal, self).__init__(apiresource)
        self._request = request

    @classmethod
    def list(cls, request, **filters):
        """Return a list of goals in Watcher

        :param request: request object
        :type  request: django.http.HttpRequest

        :param filters: key/value kwargs used as filters
        :type  filters: dict

        :return: list of goals, or an empty list if there are none
        :rtype:  list of :py:class:`~.Goal` instance
        """
        return watcherclient(request).goal.list(detail=True, **filters)

    @classmethod
    @errors_utils.handle_errors(_("Unable to retrieve goal"))
    def get(cls, request, goal):
        """Return the goal that matches the ID

        :param request: request object
        :type  request: django.http.HttpRequest

        :param goal: uuid of goal to be retrieved
        :type  goal: int

        :return: matching goal, or None if no goal matches the UUID
        :rtype:  :py:class:`~.Goal` instance
        """
        return watcherclient(request).goal.get(goal)

    @property
    def id(self):
        return self.uuid


class Strategy(base.APIDictWrapper):
    """Strategy resource."""

    _attrs = ('uuid', 'name', 'display_name', 'goal_uuid', 'goal_name',
              'created_at', 'updated_at', 'deleted_at')

    def __init__(self, apiresource, request=None):
        super(Strategy, self).__init__(apiresource)
        self._request = request

    @classmethod
    def list(cls, request, **filters):
        """Return a list of strategies in Watcher

        :param request: request object
        :type  request: django.http.HttpRequest

        :param filters: key/value kwargs used as filters
        :type  filters: dict

        :return: list of strategies, or an empty list if there are none
        :rtype:  list of :py:class:`~.Strategy` instances
        """
        return watcherclient(request).strategy.list(detail=True, **filters)

    @classmethod
    @errors_utils.handle_errors(_("Unable to retrieve strategy"))
    def get(cls, request, strategy):
        """Return the strategy that matches the UUID

        :param request: request object
        :type  request: django.http.HttpRequest

        :param strategy: uuid of strategy to be retrieved
        :type  strategy: str

        :return: matching strategy, or None if no strategy matches the UUID
        :rtype:  :py:class:`~.Strategy` instance
        """
        return watcherclient(request).strategy.get(strategy)

    @property
    def id(self):
        return self.uuid


class EfficacyIndicatorSpec(base.APIDictWrapper):

    attrs = ('name', 'description', 'unit', 'schema')


class EfficacyIndicator(base.APIDictWrapper):

    def __init__(self, indicator):
        super(EfficacyIndicator, self).__init__(indicator)
        self.value = getattr(indicator, 'value', None)
        self.name = getattr(indicator, 'name', None)
        self.description = getattr(indicator, 'description', None)
        self.unit = getattr(indicator, 'unit', None)
