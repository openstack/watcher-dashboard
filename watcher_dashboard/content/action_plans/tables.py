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
        ('audit', _("Audit ="), True),
    )
    policy_rules = (("infra-optim", "action_plan:detail"),)


class ArchiveActionPlan(horizon.tables.DeleteAction):
    verbose_name = _("Archive Action Plans")
    policy_rules = (("infra-optim", "action_plan:delete"),)

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
    policy_rules = (("infra-optim", "action_plan:update"),)
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
            msg = _('Failed to get the action plan.')
            LOG.info(msg)
            horizon.messages.warning(request, msg)

        return action_plan


def format_global_efficacy(action_plan):
    formatted_global_efficacy = None
    global_efficacy = watcher.EfficacyIndicator(action_plan.global_efficacy)
    if global_efficacy.value is not None and global_efficacy.unit:
        formatted_global_efficacy = "%(value)s %(unit)s" % dict(
            unit=global_efficacy.unit,
            value=global_efficacy.value)
    elif global_efficacy.value is not None:
        formatted_global_efficacy = global_efficacy.value

    return formatted_global_efficacy


def get_audit_link(datum):
    try:
        return urls.reverse(
            "horizon:admin:audits:detail",
            kwargs={"audit_uuid": getattr(datum, "audit_uuid", None)})
    except urls.NoReverseMatch:
        return None


class ActionPlansTable(horizon.tables.DataTable):

    name = horizon.tables.Column(
        'uuid',
        verbose_name=_("UUID"),
        link="horizon:admin:action_plans:detail")
    audit = horizon.tables.Column(
        'audit_uuid',
        verbose_name=_('Audit'),
        link=get_audit_link)
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
    efficacy = horizon.tables.Column(
        transform=format_global_efficacy,
        verbose_name=_('Efficacy'))

    def get_object_id(self, datum):
        return datum.uuid

    class Meta(object):
        name = "action_plans"
        verbose_name = _("Action Plans")
        table_actions = (
            # CancelActionPlan,
            ActionPlansFilterAction,
            StartActionPlan,
            ArchiveActionPlan,
        )
        row_actions = (
            StartActionPlan,
            # CreateActionPlans,
            ArchiveActionPlan,
            # CreateActionPlans,
            # DeleteActionPlans,
        )
        row_class = UpdateRow


class RelatedActionPlansTable(horizon.tables.DataTable):

    name = horizon.tables.Column(
        'uuid',
        verbose_name=_("UUID"),
        link="horizon:admin:action_plans:detail")
    audit = horizon.tables.Column(
        'audit_uuid',
        verbose_name=_('Audit'),
        link=get_audit_link)
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
    efficacy = horizon.tables.Column(
        transform=format_global_efficacy,
        verbose_name=_('Efficacy'))

    def get_object_id(self, datum):
        return datum.uuid

    class Meta(object):
        name = "related_action_plans"
        verbose_name = _("Related Action Plans")
        hidden_title = False
        row_actions = (
            StartActionPlan,
            ArchiveActionPlan,
        )
        row_class = UpdateRow


class RelatedEfficacyIndicatorsTable(horizon.tables.DataTable):

    name = horizon.tables.Column(
        'name',
        verbose_name=_("Name"))

    description = horizon.tables.Column(
        'description',
        verbose_name=_("Description"))

    unit = horizon.tables.Column(
        'unit',
        verbose_name=_("Unit"))

    value = horizon.tables.Column(
        'value',
        verbose_name=_("Value"))

    def get_object_id(self, datum):
        return datum.name

    class Meta(object):
        name = "related_efficacy_indicators"
        verbose_name = _("Related Efficacy Indicators")
        hidden_title = False
