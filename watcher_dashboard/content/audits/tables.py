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

from django import shortcuts
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

AUDIT_STATE_DISPLAY_CHOICES = (
    ("NO STATE", pgettext_lazy("State of an audit", u"No State")),
    ("ONGOING", pgettext_lazy("State of an audit", u"On Going")),
    ("SUCCEEDED", pgettext_lazy("State of an audit", u"Succeeeded")),
    ("SUBMITTED", pgettext_lazy("State of an audit", u"Submitted")),
    ("FAILED", pgettext_lazy("State of an audit", u"Failed")),
    ("DELETED", pgettext_lazy("State of an audit", u"Deleted")),
    ("PENDING", pgettext_lazy("State of an audit", u"Pending")),
)


class AuditsFilterAction(horizon.tables.FilterAction):
    # server = choices query = text
    filter_type = "server"
    filter_choices = (
        ('audit_template', _("Audit Template ="), True),
    )
    policy_rules = (("infra-optim", "audit:detail"),)


class CreateAudit(horizon.tables.LinkAction):
    name = "create_audit"
    verbose_name = _("Create Audit")
    url = "horizon:admin:audits:create"
    classes = ("ajax-modal", "btn-launch")
    policy_rules = (("infra-optim", "audit:create"),)


class GoToActionPlan(horizon.tables.Action):
    name = "go_to_action_plan"
    verbose_name = _("Go to Action Plan")
    url = "horizon:admin:action_plans:detail"
    policy_rules = (("infra-optim", "action_plan:detail"),)

    def allowed(self, request, audit):
        return audit or audit.state in ("SUCCEEDED", )

    def single(self, table, request, audit_id):
        try:
            action_plans = watcher.ActionPlan.list(
                request,
                audit=audit_id)
        except Exception:
            horizon.exceptions.handle(
                request,
                _("Unable to retrieve action_plan information."))
            return "javascript:void(0);"

        return shortcuts.redirect(urls.reverse(
            self.url,
            args=[action_plans[0].uuid]))


class ArchiveAudits(horizon.tables.DeleteAction):
    verbose_name = _("Archive Audits")
    policy_rules = (("infra-optim", "audit:delete"),)

    def allowed(self, request, audit):
        return audit or audit.state not in ("ONGOING", "PENDING")

    @staticmethod
    def action_present(count):
        return ungettext_lazy(
            "Archive Audit",
            "Archive Audits",
            count
        )

    @staticmethod
    def action_past(count):
        return ungettext_lazy(
            "Archived Audit",
            "Archived Audits",
            count
        )

    def delete(self, request, obj_id):
        watcher.Audit.delete(request, obj_id)


class AuditsTable(horizon.tables.DataTable):
    uuid = horizon.tables.Column(
        'uuid',
        verbose_name=_("UUID"),
        link="horizon:admin:audits:detail")
    name = horizon.tables.Column(
        'name',
        verbose_name=_("Name"),
        link="horizon:admin:audits:detail")
    goal = horizon.tables.Column(
        'goal_name',
        verbose_name=_('Goal'))
    strategy = horizon.tables.Column(
        'strategy_name',
        verbose_name=_('Strategy'))
    audit_type = horizon.tables.Column(
        'audit_type',
        verbose_name=_('Audit Type'))
    auto_trigger = horizon.tables.Column(
        'auto_trigger',
        verbose_name=_('Auto Trigger'))
    status = horizon.tables.Column(
        'state',
        verbose_name=_('State'),
        status=True,
        status_choices=AUDIT_STATE_DISPLAY_CHOICES)

    def get_object_id(self, datum):
        return datum.uuid

    class Meta(object):
        name = "audits"
        verbose_name = _("Audits")
        launch_actions = (CreateAudit,)
        table_actions = launch_actions + (
            AuditsFilterAction,
        )
        row_actions = (
            GoToActionPlan,
            ArchiveAudits,
        )


class RelatedAuditsTable(horizon.tables.DataTable):
    name = horizon.tables.Column(
        'uuid',
        verbose_name=_("UUID"),
        link="horizon:admin:audits:detail")
    audit_template = horizon.tables.Column(
        'audit_template_name',
        verbose_name=_('Audit Template'),
        filters=(title, filters.replace_underscores))
    status = horizon.tables.Column(
        'state',
        verbose_name=_('State'),
        status=True,
        status_choices=AUDIT_STATE_DISPLAY_CHOICES)

    def get_object_id(self, datum):
        return datum.uuid

    class Meta(object):
        name = "audits"
        verbose_name = _("Related audits")
        hidden_title = False
