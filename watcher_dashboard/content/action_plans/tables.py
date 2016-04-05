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
from django.utils.translation import ungettext_lazy
import horizon.exceptions
import horizon.messages
import horizon.tables
from horizon.utils import filters

from watcher_dashboard.api import watcher

LOG = logging.getLogger(__name__)

ACTION_PLAN_STATE_DISPLAY_CHOICES = (
    ("NO STATE", pgettext_lazy("State of an action plan", u"No State")),
    ("ONGOING", pgettext_lazy("State of an action plan", u"On Going")),
    ("SUCCEEDED", pgettext_lazy("State of an action plan", u"Succeeded")),
    ("SUBMITTED", pgettext_lazy("State of an action plan", u"Submitted")),
    ("FAILED", pgettext_lazy("State of an action plan", u"Failed")),
    ("DELETED", pgettext_lazy("State of an action plan", u"Deleted")),
    ("RECOMMENDED", pgettext_lazy("State of an action plan", u"Recommended")),
)


class ActionPlansFilterAction(horizon.tables.FilterAction):
    # server = choices query = text
    filter_type = "server"
    filter_choices = (
        ('audit_filter', _("Audit ="), True),
    )


class ArchiveActionPlan(horizon.tables.BatchAction):
    name = "archive_action_plans"
    # policy_rules = (("compute", "compute:delete"),)
    help_text = _("Archive an action plan.")

    @staticmethod
    def action_present(count):
        return ungettext_lazy(
            u"Archive Action Plan",
            u"Archive Action Plans",
            count
        )

    @staticmethod
    def action_past(count):
        return ungettext_lazy(
            u"Action Plan archived",
            u"Action Plans archived",
            count
        )

    def action(self, request, obj_id):
        watcher.ActionPlan.delete(request, obj_id)


class StartActionPlan(horizon.tables.BatchAction):
    name = "start_action_plan"
    classes = ('btn-confirm',)
    # policy_rules = (("compute", "compute:delete"),)
    help_text = _("Execute an action plan.")

    @staticmethod
    def action_present(count):
        return ungettext_lazy(
            u"Start Action Plan",
            u"Start Action Plans",
            count
        )

    @staticmethod
    def action_past(count):
        return ungettext_lazy(
            u"Action Plan started",
            u"Action Plans started",
            count
        )

    def action(self, request, action_plan_id):
        try:
            watcher.ActionPlan.start(request, action_plan_id)
        except Exception:
            msg = _('Failed to start the action plan.')
            LOG.info(msg)
            horizon.messages.warning(request, msg)

    def allowed(self, request, action_plan):
        return ((action_plan is None) or
                (action_plan.state in ("RECOMMENDED", "FAILED")))


class UpdateRow(horizon.tables.Row):
    ajax = True

    def get_data(self, request, action_plan_id):
        action_plan = None

        try:
            action_plan = watcher.Action.get(request, action_plan_id)
        except Exception:
            msg = _('Failed to get the action_plan.')
            LOG.info(msg)
            horizon.messages.warning(request, msg)

        return action_plan


class ActionPlansTable(horizon.tables.DataTable):
    name = horizon.tables.Column(
        'uuid',
        verbose_name=_("UUID"),
        link="horizon:admin:action_plans:detail")
    audit = horizon.tables.Column(
        'audit_uuid',
        verbose_name=_('Audit'),
        filters=(title, filters.replace_underscores))
    updated_at = horizon.tables.Column(
        'updated_at',
        filters=(filters.parse_isotime,
                 filters.timesince_sortable),
        verbose_name=_("Updated At"))
    status = horizon.tables.Column(
        'state',
        verbose_name=_('State'),
        status=True,
        status_choices=ACTION_PLAN_STATE_DISPLAY_CHOICES)

    def get_object_id(self, datum):
        return datum.uuid

    class Meta(object):
        name = "action_plans"
        verbose_name = _("ActionPlans")
        table_actions = (
            # CancelActionPlan,
            ActionPlansFilterAction,
        )
        row_actions = (
            StartActionPlan,
            # CreateActionPlans,
            ArchiveActionPlan,
            # CreateActionPlans,
            # DeleteActionPlans,
        )
        row_class = UpdateRow
