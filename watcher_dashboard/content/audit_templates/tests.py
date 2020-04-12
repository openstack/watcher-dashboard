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

from unittest import mock

from django import urls

from watcher_dashboard import api
from watcher_dashboard.test import helpers as test

INDEX_URL = urls.reverse(
    'horizon:admin:audit_templates:index')
CREATE_URL = urls.reverse(
    'horizon:admin:audit_templates:create')
DETAILS_VIEW = 'horizon:admin:audit_templates:detail'


class AuditTemplatesTest(test.BaseAdminViewTests):

    def setUp(self):
        super(AuditTemplatesTest, self).setUp()
        self.goal_list = self.goals.list()
        self.strategy_list = self.strategies.list()

    @mock.patch.object(api.watcher.AuditTemplate, 'list')
    def test_index(self, mock_list):
        mock_list.return_value = self.audit_templates.list()

        res = self.client.get(INDEX_URL)
        self.assertTemplateUsed(res, 'infra_optim/audit_templates/index.html')
        audit_templates = res.context['audit_templates_table'].data
        self.assertCountEqual(audit_templates, self.audit_templates.list())

    @mock.patch.object(api.watcher.AuditTemplate, 'list')
    def test_audit_template_list_unavailable(self, mock_list):
        mock_list.side_effect = self.exceptions.watcher

        resp = self.client.get(INDEX_URL)
        self.assertMessageCount(resp, error=1, warning=0)

    @mock.patch.object(api.watcher.Strategy, 'list')
    @mock.patch.object(api.watcher.Goal, 'list')
    def test_create_get(self, m_goal_list, m_strategy_list):
        m_goal_list.return_value = self.goal_list
        m_strategy_list.return_value = self.strategy_list
        res = self.client.get(CREATE_URL)
        self.assertTemplateUsed(res, 'infra_optim/audit_templates/create.html')

    @mock.patch.object(api.watcher.Strategy, 'list')
    @mock.patch.object(api.watcher.Goal, 'list')
    @mock.patch.object(api.watcher.AuditTemplate, 'create')
    def test_create_post(self, m_audit_create, m_goal_list, m_strategy_list):
        at = self.audit_templates.first()
        form_data = {
            'name': at.name,
            'goal': at.goal_uuid,
            'strategy': at.strategy_uuid,
            'description': at.description,
            'scope': at.scope,
        }
        m_goal_list.return_value = self.goal_list
        m_strategy_list.return_value = self.strategy_list
        m_audit_create.return_value = at

        res = self.client.post(CREATE_URL, form_data)
        self.assertNoFormErrors(res)
        self.assertRedirectsNoFollow(res, INDEX_URL)

    @mock.patch.object(api.watcher.AuditTemplate, 'get')
    def test_details(self, m_get):
        at = self.audit_templates.first()
        at_id = at.uuid
        m_get.return_value = at

        DETAILS_URL = urls.reverse(DETAILS_VIEW, args=[at_id])
        res = self.client.get(DETAILS_URL)
        self.assertTemplateUsed(res,
                                'infra_optim/audit_templates/details.html')
        audit_templates = res.context['audit_template']
        self.assertCountEqual([audit_templates], [at])

    @mock.patch.object(api.watcher.AuditTemplate, 'get')
    def test_details_exception(self, m_get):
        at = self.audit_templates.first()
        at_id = at.uuid
        m_get.side_effect = self.exceptions.watcher

        DETAILS_URL = urls.reverse(DETAILS_VIEW, args=[at_id])
        res = self.client.get(DETAILS_URL)
        self.assertRedirectsNoFollow(res, INDEX_URL)

    @mock.patch.object(api.watcher.AuditTemplate, 'delete')
    @mock.patch.object(api.watcher.AuditTemplate, 'list')
    def test_delete(self, m_list, m_del):
        at_list = self.audit_templates.list()
        at = self.audit_templates.first()
        at_id = at.uuid
        m_list.return_value = at_list

        form_data = {'action': 'audit_templates__delete',
                     'object_ids': at_id}

        res = self.client.post(INDEX_URL, form_data)
        self.assertRedirectsNoFollow(res, INDEX_URL)
