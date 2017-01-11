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


class GoalsTable(horizon.tables.DataTable):
    uuid = horizon.tables.Column(
        'uuid',
        verbose_name=_("UUID"),
        link="horizon:admin:goals:detail")

    name = horizon.tables.Column(
        'name',
        verbose_name=_('Name'))

    display_name = horizon.tables.Column(
        'display_name',
        verbose_name=_('Verbose Name'))

    def get_object_id(self, datum):
        return datum.uuid

    class Meta(object):
        name = "goals"
        verbose_name = _("Goals")


class EfficacySpecificationTable(horizon.tables.DataTable):

    name = horizon.tables.Column(
        'name',
        verbose_name=_("Name"))

    description = horizon.tables.Column(
        'description',
        verbose_name=_("Description"))

    unit = horizon.tables.Column(
        'unit',
        verbose_name=_("Unit"))

    schema = horizon.tables.Column(
        'schema',
        verbose_name=_("Schema"))

    def get_object_id(self, datum):
        return datum.name

    class Meta(object):
        name = "efficacy_specification"
        verbose_name = _("Efficacy specification")
        hidden_title = False
