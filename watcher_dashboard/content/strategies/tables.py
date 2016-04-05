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

from django.template.defaultfilters import title  # noqa
from django.utils.translation import ugettext_lazy as _
import horizon.exceptions
import horizon.messages
import horizon.tables
from horizon.utils import filters


class StrategiesTable(horizon.tables.DataTable):
    uuid = horizon.tables.Column(
        'uuid',
        verbose_name=_("UUID"),
        link="horizon:admin:strategies:detail")
    display_name = horizon.tables.Column(
        'display_name',
        verbose_name=_('Name'),
        filters=(title, filters.replace_underscores))
    goal_uuid = horizon.tables.Column(
        'goal_uuid',
        verbose_name=_("Goal UUID"),
    )

    def get_object_id(self, datum):
        return datum.uuid

    class Meta(object):
        name = "strategies"
        verbose_name = _("Strategies")
