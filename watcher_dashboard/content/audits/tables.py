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

from django.core import urlresolvers
from django import shortcuts
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
    name = "launch_audit"
    verbose_name = _("Launch Audit")
    url = "horizon:admin:audits:create"
    classes = ("ajax-modal", "btn-launch")
    policy_rules = (("infra-optim", "audit:create"),)


class GoToActionPlan(horizon.tables.Action):
    name = "go_to_action_plan"
    verbose_name = _("Go to Action Plan")
    url = "horizon:admin:action_plans:detail"
    policy_rules = (("infra-optim", "action_plan:detail"),)

    def allowed(self, request, audit):
        return audit or audit.state in ("SUCCEEEDED", )

    def single(self, table, request, audit_id):
        try:
            action_plans = watcher.ActionPlan.list(
                request,
                audit_filter=audit_id)
        except Exception:
            horizon.exceptions.handle(
                request,
                _("Unable to retrieve action_plan information."))
            return "javascript:void(0);"

        return shortcuts.redirect(urlresolvers.reverse(
            self.url,
            args=[action_plans[0].uuid]))


class GoToAuditTemplate(horizon.tables.Action):
    name = "go_to_audit_template"
    verbose_name = _("Go to Audit Template")
    url = "horizon:admin:audit_templates:detail"
    policy_rules = (("infra-optim", "audit:get_one"),)
    # classes = ("ajax-modal", "btn-launch")
    # icon = "send"

    def allowed(self, request, audit):
        return audit or audit.state in ("SUCCEEEDED", )

    def single(self, table, request, audit_id):
        try:
            audit = watcher.Audit.get(
                request, audit_id=audit_id)
        except Exception:
            horizon.exceptions.handle(
                request,
                _("Unable to retrieve audit information."))
            return "javascript:void(0);"

        return shortcuts.redirect(urlresolvers.reverse(
            self.url,
            args=[audit.audit_template_uuid]))


class DeleteAudits(horizon.tables.DeleteAction):
    verbose_name = _("Delete Audits")

    @staticmethod
    def action_present(count):
        return ungettext_lazy(
            "Delete Audit",
            "Delete Audits",
            count
        )

    @staticmethod
    def action_past(count):
        return ungettext_lazy(
            "Deleted Audit",
            "Deleted Audits",
            count
        )

    def delete(self, request, obj_id):
        watcher.Audit.delete(request, obj_id)


class AuditsTable(horizon.tables.DataTable):
    name = horizon.tables.Column(
        'uuid',
        verbose_name=_("UUID"),
        link="horizon:admin:audits:detail")
    audit_template = horizon.tables.Column(
        'audit_template_name',
        verbose_name=_('Audit Template'))
    audit_type = horizon.tables.Column(
        'audit_type',
        verbose_name=_('Audit Type'))
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
            # CancelAudit,
            AuditsFilterAction,
            # ArchiveAudits,
        )
        row_actions = (
            GoToActionPlan,
            GoToAuditTemplate,
            # CreateAudits,
            # ArchiveAudits,
            # CreateAudits,
            DeleteAudits,
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
