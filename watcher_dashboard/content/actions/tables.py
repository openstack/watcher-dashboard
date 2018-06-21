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

from django.template.defaultfilters import title  # noqa
from django import urls
from django.utils.translation import pgettext_lazy
from django.utils.translation import ugettext_lazy as _
import horizon.exceptions
import horizon.messages
import horizon.tables
from horizon.utils import filters

from watcher_dashboard.api import watcher

LOG = logging.getLogger(__name__)


ACTION_STATE_DISPLAY_CHOICES = (
    ("NO STATE", pgettext_lazy("Power state of an Instance", u"No State")),
    ("ONGOING", pgettext_lazy("Power state of an Instance", u"On Going")),
    ("SUCCEEDED", pgettext_lazy("Power state of an Instance", u"Succeeded")),
    ("CANCELLED", pgettext_lazy("Power state of an Instance", u"Cancelled")),
    ("FAILED", pgettext_lazy("Power state of an Instance", u"Failed")),
    ("DELETED", pgettext_lazy("Power state of an Instance", u"Deleted")),
    ("PENDING", pgettext_lazy("Power state of an Instance", u"Pending")),
)


class UpdateRow(horizon.tables.Row):
    ajax = True

    def get_data(self, request, action_id):
        action = None
        try:
            action = watcher.Action.get(request, action_id)
        except Exception:
            msg = _('Failed to get the action.')
            LOG.info(msg)
            horizon.messages.warning(request, msg)

        return action


class ActionsFilterAction(horizon.tables.FilterAction):
    filter_type = "server"
    filter_choices = (('action_plan', _("Action Plan ID ="), True),)
    policy_rules = (("infra-optim", "action:detail"),)


def get_action_plan_link(datum):
    try:
        return urls.reverse(
            "horizon:admin:action_plans:detail",
            kwargs={"action_plan_uuid": getattr(
                datum, "action_plan_uuid", None)})
    except urls.NoReverseMatch:
        return None


class ActionsTable(horizon.tables.DataTable):
    name = horizon.tables.Column(
        'uuid',
        verbose_name=_("UUID"),
        link="horizon:admin:actions:detail")
    action_type = horizon.tables.Column(
        'action_type',
        verbose_name=_('Type'),
        filters=(title, filters.replace_underscores))
    state = horizon.tables.Column(
        'state',
        verbose_name=_('State'),
        status_choices=ACTION_STATE_DISPLAY_CHOICES)
    action_plan = horizon.tables.Column(
        'action_plan_uuid',
        verbose_name=_('Action Plan'),
        link=get_action_plan_link)

    def get_object_id(self, datum):
        return datum.uuid

    class Meta(object):
        name = "wactions"
        verbose_name = _("Actions")
        table_actions = (ActionsFilterAction, )
        row_class = UpdateRow


class RelatedActionsTable(horizon.tables.DataTable):
    """Identical to the index table but with different Meta"""
    name = horizon.tables.Column(
        'uuid',
        verbose_name=_("UUID"),
        link="horizon:admin:actions:detail")
    action_type = horizon.tables.Column(
        'action_type',
        verbose_name=_('Type'),
        filters=(title, filters.replace_underscores))
    state = horizon.tables.Column(
        'state',
        verbose_name=_('State'),
        status_choices=ACTION_STATE_DISPLAY_CHOICES)
    action_plan = horizon.tables.Column(
        'action_plan_uuid',
        verbose_name=_('Action Plan'),
        link=get_action_plan_link)

    def get_object_id(self, datum):
        return datum.uuid

    class Meta(object):
        name = "related_wactions"
        verbose_name = _("Related Actions")
        hidden_title = False


class ActionParametersTable(horizon.tables.DataTable):
    name = horizon.tables.Column(
        'name',
        verbose_name=_("Parameter name"))
    value = horizon.tables.Column(
        'value',
        verbose_name=_('Parameter value'))

    def get_object_id(self, datum):
        return datum.name

    class Meta(object):
        name = "parameters"
        verbose_name = _("Related parameters")
        hidden_title = False
