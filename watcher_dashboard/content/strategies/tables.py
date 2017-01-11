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
import horizon.exceptions
import horizon.messages
import horizon.tables


class StrategiesFilterAction(horizon.tables.FilterAction):
    # server = choices query = text
    filter_type = "server"
    filter_choices = (
        ('goal', _("Goal ="), True),
    )
    policy_rules = (("infra-optim", "strategy:detail"),)


class StrategiesTable(horizon.tables.DataTable):

    uuid = horizon.tables.Column(
        'uuid',
        verbose_name=_("UUID"),
        link="horizon:admin:strategies:detail")

    name = horizon.tables.Column(
        'name',
        verbose_name=_('Name'))

    display_name = horizon.tables.Column(
        'display_name',
        verbose_name=_('Verbose Name'))

    goal = horizon.tables.Column(
        'goal_name',
        verbose_name=_("Goal"),
    )

    def get_object_id(self, datum):
        return datum.uuid

    class Meta(object):
        name = "strategies"
        verbose_name = _("Strategies")
        table_actions = (
            StrategiesFilterAction,
        )


class RelatedStrategiesTable(horizon.tables.DataTable):

    uuid = horizon.tables.Column(
        'uuid',
        verbose_name=_("UUID"),
        link="horizon:admin:strategies:detail")

    name = horizon.tables.Column(
        'name',
        verbose_name=_('Name'))

    display_name = horizon.tables.Column(
        'display_name',
        verbose_name=_('Verbose Name'))

    goal = horizon.tables.Column(
        'goal_name',
        verbose_name=_("Goal"),
    )

    def get_object_id(self, datum):
        return datum.uuid

    class Meta(object):
        name = "related_strategies"
        verbose_name = _("Related strategies")
        hidden_title = False
