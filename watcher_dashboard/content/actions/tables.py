# -*- encoding: utf-8 -*-
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


class ActionsTable(horizon.tables.DataTable):
    name = horizon.tables.Column(
        'uuid',
        verbose_name=_("UUID"))
    action_type = horizon.tables.Column(
        'action_type',
        verbose_name=_('Type'),
        filters=(title, filters.replace_underscores))
    description = horizon.tables.Column(
        'description',
        verbose_name=_('Description'))
    state = horizon.tables.Column(
        'state',
        verbose_name=_('State'),
        status_choices=ACTION_STATE_DISPLAY_CHOICES)

    next_action = horizon.tables.Column(
        'next_uuid',
        verbose_name=_('Next Action'))

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
        verbose_name=_("UUID"))
    action_type = horizon.tables.Column(
        'action_type',
        verbose_name=_('Type'),
        filters=(title, filters.replace_underscores))
    description = horizon.tables.Column(
        'description',
        verbose_name=_('Description'))
    state = horizon.tables.Column(
        'state',
        verbose_name=_('State'),
        status_choices=ACTION_STATE_DISPLAY_CHOICES)

    next_action = horizon.tables.Column(
        'next_uuid',
        verbose_name=_('Next Action'))

    def get_object_id(self, datum):
        return datum.uuid

    class Meta(object):
        name = "related_wactions"
        verbose_name = _("Related Actions")
        hidden_title = False
