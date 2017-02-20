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

from django.core import urlresolvers
from django import http
from mox3.mox import IsA  # noqa

from watcher_dashboard import api
from watcher_dashboard.test import helpers as test

INDEX_URL = urlresolvers.reverse(
    'horizon:admin:audit_templates:index')
CREATE_URL = urlresolvers.reverse(
    'horizon:admin:audit_templates:create')
DETAILS_VIEW = 'horizon:admin:audit_templates:detail'


class AuditTemplatesTest(test.BaseAdminViewTests):

    def setUp(self):
        super(AuditTemplatesTest, self).setUp()
        self.goal_list = self.goals.list()
        self.strategy_list = self.strategies.list()

    @test.create_stubs({api.watcher.AuditTemplate: ('list',)})
    def test_index(self):
        search_opts = {}
        api.watcher.AuditTemplate.list(
            IsA(http.HttpRequest),
            **search_opts).MultipleTimes().AndReturn(
            self.audit_templates.list())
        self.mox.ReplayAll()

        res = self.client.get(INDEX_URL)
        self.assertTemplateUsed(res, 'infra_optim/audit_templates/index.html')
        audit_templates = res.context['audit_templates_table'].data
        self.assertItemsEqual(audit_templates, self.audit_templates.list())

    @test.create_stubs({api.watcher.AuditTemplate: ('list',)})
    def test_audit_template_list_unavailable(self):
        search_opts = None
        api.watcher.AuditTemplate.list(
            IsA(http.HttpRequest),
            filter=search_opts).MultipleTimes().AndRaise(
            self.exceptions.watcher)
        self.mox.ReplayAll()

        resp = self.client.get(INDEX_URL)
        self.assertMessageCount(resp, error=1, warning=0)

    @test.create_stubs({api.watcher.Strategy: ('list',)})
    @test.create_stubs({api.watcher.Goal: ('list',)})
    def test_create_get(self):
        api.watcher.Goal.list(
            IsA(http.HttpRequest)).AndReturn(self.goal_list)
        api.watcher.Strategy.list(
            IsA(http.HttpRequest)).AndReturn(self.strategy_list)
        self.mox.ReplayAll()
        res = self.client.get(CREATE_URL)
        self.assertTemplateUsed(res, 'infra_optim/audit_templates/create.html')

    @test.create_stubs({api.watcher.Strategy: ('list',)})
    @test.create_stubs({api.watcher.Goal: ('list',)})
    @test.create_stubs({api.watcher.AuditTemplate: ('create',)})
    def test_create_post(self):
        at = self.audit_templates.first()
        form_data = {
            'name': at.name,
            'goal': at.goal_uuid,
            'strategy': at.strategy_uuid,
            'description': at.description,
            'scope': at.scope,
        }
        api.watcher.Goal.list(
            IsA(http.HttpRequest)).AndReturn(self.goal_list)
        api.watcher.Strategy.list(
            IsA(http.HttpRequest)).AndReturn(self.strategy_list)

        api.watcher.AuditTemplate.create(
            IsA(http.HttpRequest), **form_data).AndReturn(at)
        self.mox.ReplayAll()

        res = self.client.post(CREATE_URL, form_data)
        self.assertNoFormErrors(res)
        self.assertRedirectsNoFollow(res, INDEX_URL)

    @test.create_stubs({api.watcher.AuditTemplate: ('get',)})
    def test_details(self):
        at = self.audit_templates.first()
        at_id = at.uuid
        api.watcher.AuditTemplate.get(
            IsA(http.HttpRequest), at_id).\
            MultipleTimes().AndReturn(at)
        self.mox.ReplayAll()
        DETAILS_URL = urlresolvers.reverse(DETAILS_VIEW, args=[at_id])
        res = self.client.get(DETAILS_URL)
        self.assertTemplateUsed(res,
                                'infra_optim/audit_templates/details.html')
        audit_templates = res.context['audit_template']
        self.assertItemsEqual([audit_templates], [at])

    @test.create_stubs({api.watcher.AuditTemplate: ('get',)})
    def test_details_exception(self):
        at = self.audit_templates.first()
        at_id = at.uuid
        api.watcher.AuditTemplate.get(IsA(http.HttpRequest), at_id) \
            .AndRaise(self.exceptions.watcher)

        self.mox.ReplayAll()

        DETAILS_URL = urlresolvers.reverse(DETAILS_VIEW, args=[at_id])
        res = self.client.get(DETAILS_URL)
        self.assertRedirectsNoFollow(res, INDEX_URL)

    @test.create_stubs({api.watcher.AuditTemplate: ('delete', 'list')})
    def test_delete(self):
        search_opts = {}
        at_list = self.audit_templates.list()
        at = self.audit_templates.first()
        at_id = at.uuid
        api.watcher.AuditTemplate.list(
            IsA(http.HttpRequest),
            **search_opts).MultipleTimes().AndReturn(at_list)
        api.watcher.AuditTemplate.delete(IsA(http.HttpRequest), at_id)
        self.mox.ReplayAll()

        form_data = {'action': 'audit_templates__delete',
                     'object_ids': at_id}

        res = self.client.post(INDEX_URL, form_data)
        self.assertRedirectsNoFollow(res, INDEX_URL)
