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

from django.utils.translation import ugettext_lazy as _
from django.utils.translation import ungettext_lazy
import horizon.exceptions
import horizon.messages
import horizon.tables

from watcher_dashboard.api import watcher


class CreateAuditTemplates(horizon.tables.LinkAction):
    name = "create"
    verbose_name = _("Create Template")
    url = "horizon:admin:audit_templates:create"
    classes = ("ajax-modal", "btn-launch")
    policy_rules = (("infra-optim", "audit_template:create"),)


class AuditTemplatesFilterAction(horizon.tables.FilterAction):
    filter_type = "server"
    filter_choices = (
        ('goal', _("Goal ="), True),
        ('strategy', _("Strategy ="), True),
    )
    policy_rules = (("infra-optim", "audit_template:detail"),)


class LaunchAudit(horizon.tables.BatchAction):
    name = "launch_audit"
    verbose_name = _("Launch Audit")
    data_type_singular = _("Launch Audit")
    data_type_plural = _("Launch Audits")
    success_url = "horizon:admin:audits:index"
    policy_rules = (("infra-optim", "audit:create"),)

    @staticmethod
    def action_present(count):
        return ungettext_lazy(
            "Launch Audit",
            "Launch Audits",
            count
        )

    @staticmethod
    def action_past(count):
        return ungettext_lazy(
            "Launched Audit",
            "Launched Audits",
            count
        )

    def action(self, request, obj_id):
        params = {'audit_template_uuid': obj_id}
        params['audit_type'] = 'ONESHOT'
        params['auto_trigger'] = False
        watcher.Audit.create(request, **params)


class ArchiveAuditTemplates(horizon.tables.DeleteAction):
    verbose_name = _("Archive Templates")
    policy_rules = (("infra-optim", "audit_template:delete"),)

    @staticmethod
    def action_present(count):
        return ungettext_lazy(
            "Archive Template",
            "Archive Templates",
            count
        )

    @staticmethod
    def action_past(count):
        return ungettext_lazy(
            "Archived Template",
            "Archived Templates",
            count
        )

    def delete(self, request, obj_id):
        watcher.AuditTemplate.delete(request, obj_id)


class AuditTemplatesTable(horizon.tables.DataTable):
    name = horizon.tables.Column(
        'name',
        verbose_name=_("Name"),
        link="horizon:admin:audit_templates:detail")
    goal = horizon.tables.Column(
        'goal_name',
        verbose_name=_('Goal'),
        status=True,
    )
    strategy = horizon.tables.Column(
        'strategy_name',
        verbose_name=_('Strategy'),
        status=True,
    )

    def get_object_id(self, datum):
        return datum.uuid

    class Meta(object):
        name = "audit_templates"
        verbose_name = _("Audit Templates")
        table_actions = (
            CreateAuditTemplates,
            AuditTemplatesFilterAction,
            LaunchAudit,
            ArchiveAuditTemplates,
        )
        row_actions = (
            LaunchAudit,
            ArchiveAuditTemplates,
        )
