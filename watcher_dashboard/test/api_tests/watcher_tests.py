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

from __future__ import absolute_import
from watcher_dashboard import api
from watcher_dashboard.test import helpers as test


class WatcherAPITests(test.APITestCase):

    def test_audit_template_list(self):
        audit_templates = {'audit_templates': self.api_audit_templates.list()}
        watcherclient = self.stub_watcherclient()

        watcherclient.audit_template = self.mox.CreateMockAnything()
        watcherclient.audit_template.list(name=None).AndReturn(audit_templates)
        self.mox.ReplayAll()

        ret_val = api.watcher.AuditTemplate.list(self.request, filter=None)
        for n in ret_val:
            self.assertTrue(type(ret_val), 'dict')

    def test_audit_template_list_with_filters(self):
        search_opts = 'Audit Template 1'
        audit_templates = self.api_audit_templates.filter(name=search_opts)
        watcherclient = self.stub_watcherclient()

        watcherclient.audit_template = self.mox.CreateMockAnything()

        watcherclient.audit_template.list(name=search_opts)\
            .AndReturn(audit_templates)
        self.mox.ReplayAll()

        ret_val = api.watcher.AuditTemplate\
            .list(self.request, filter=search_opts)
        for n in ret_val:
            self.assertTrue(type(ret_val), 'dict')
        self.assertEqual(ret_val, audit_templates)

    def test_audit_template_get(self):
        audit_template = {'audit_template': self.api_audit_templates.first()}
        audit_template_id = self.api_audit_templates.first()['uuid']

        watcherclient = self.stub_watcherclient()
        watcherclient.audit_template = self.mox.CreateMockAnything()
        watcherclient.audit_template.get(
            audit_template_id=audit_template_id).AndReturn(audit_template)
        self.mox.ReplayAll()

        ret_val = api.watcher.AuditTemplate.get(self.request,
                                                audit_template_id)
        self.assertTrue(type(ret_val), 'dict')

    def test_audit_template_create(self):
        audit_template = {'audit_template': self.api_audit_templates.first()}
        name = self.api_audit_templates.first()['name']
        goal = self.api_audit_templates.first()['goal']
        description = self.api_audit_templates.first()['description']
        host_aggregate = self.api_audit_templates.first()['host_aggregate']

        watcherclient = self.stub_watcherclient()
        watcherclient.audit_template = self.mox.CreateMockAnything()
        watcherclient.audit_template.create(
            name=name,
            goal=goal,
            description=description,
            host_aggregate=host_aggregate).AndReturn(audit_template)
        self.mox.ReplayAll()

        ret_val = api.watcher.AuditTemplate.create(
            self.request, name, goal, description, host_aggregate)
        self.assertTrue(type(ret_val), 'dict')

    def test_audit_template_patch(self):
        audit_template = {'audit_template': self.api_audit_templates.first()}
        audit_template_id = self.api_audit_templates.first()['uuid']
        form_data = {'name': 'new Audit Template 1'}

        watcherclient = self.stub_watcherclient()
        watcherclient.audit_template = self.mox.CreateMockAnything()
        watcherclient.audit_template.patch(
            audit_template_id,
            [{'name': 'name', 'value': 'new Audit Template 1'}]
        ).AndReturn(audit_template)
        self.mox.ReplayAll()

        ret_val = api.watcher.AuditTemplate.patch(
            self.request, audit_template_id,
            form_data)
        self.assertTrue(type(ret_val), 'dict')

    def test_audit_template_delete(self):
        audit_template_list = self.api_audit_templates.list()
        audit_template_id = self.api_audit_templates.first()['uuid']
        deleted_at_list = self.api_audit_templates.delete()

        watcherclient = self.stub_watcherclient()
        watcherclient.audit_template = self.mox.CreateMockAnything()
        watcherclient.audit_template.delete(
            audit_template_id=audit_template_id)
        self.mox.ReplayAll()
        api.watcher.AuditTemplate.delete(self.request,
                                         audit_template_id)
        self.assertEqual(audit_template_list, deleted_at_list)
        self.assertEqual(len(audit_template_list), len(deleted_at_list))

    def test_audit_list(self):
        audits = {'audits': self.api_audits.list()}

        watcherclient = self.stub_watcherclient()

        watcherclient.audit = self.mox.CreateMockAnything()
        watcherclient.audit.list(audit_template=None).AndReturn(audits)
        self.mox.ReplayAll()

        ret_val = api.watcher.Audit.list(
            self.request,
            audit_template_filter=None)
        for n in ret_val:
            self.assertIsInstance(n, api.watcher.Audit)

    def test_audit_get(self):
        audit = {'audit': self.api_audits.first()}
        audit_id = self.api_audits.first()['id']

        watcherclient = self.stub_watcherclient()
        watcherclient.audit = self.mox.CreateMockAnything()
        watcherclient.audit.get(
            audit_id=audit_id).AndReturn(audit)
        self.mox.ReplayAll()

        ret_val = api.watcher.Audit.get(self.request, audit_id)
        self.assertIsInstance(ret_val, api.watcher.Audit)

    def test_audit_create(self):
        audit = {'audit': self.api_audits.first()}
        audit_template_id = self.api_audit_templates.first()['uuid']

        deadline = self.api_audits.first()['deadline']
        _type = self.api_audits.first()['type']
        audit_template_uuid = audit_template_id

        watcherclient = self.stub_watcherclient()
        watcherclient.audit = self.mox.CreateMockAnything()
        watcherclient.audit.create(
            audit_template_uuid=audit_template_uuid,
            type=_type,
            deadline=deadline).AndReturn(audit)
        self.mox.ReplayAll()

        ret_val = api.watcher.Audit.create(
            self.request, audit_template_uuid, _type, deadline)
        self.assertIsInstance(ret_val, api.watcher.Audit)

    def test_audit_delete(self):
        audit_id = self.api_audits.first()['id']

        watcherclient = self.stub_watcherclient()
        watcherclient.audit = self.mox.CreateMockAnything()
        watcherclient.audit.delete(
            audit_id=audit_id)
        self.mox.ReplayAll()

        api.watcher.Audit.delete(self.request, audit_id)

    def test_action_plan_list(self):
        action_plans = {'action_plans': self.api_action_plans.list()}

        watcherclient = self.stub_watcherclient()

        watcherclient.action_plan = self.mox.CreateMockAnything()
        watcherclient.action_plan.list(audit=None).AndReturn(action_plans)
        self.mox.ReplayAll()

        ret_val = api.watcher.ActionPlan.list(
            self.request,
            audit_filter=None)
        for n in ret_val:
            self.assertIsInstance(n, api.watcher.ActionPlan)

    def test_action_plan_get(self):
        action_plan = {'action_plan': self.api_action_plans.first()}
        action_plan_id = self.api_action_plans.first()['id']

        watcherclient = self.stub_watcherclient()
        watcherclient.action_plan = self.mox.CreateMockAnything()
        watcherclient.action_plan.get(
            action_plan_id=action_plan_id).AndReturn(action_plan)
        self.mox.ReplayAll()

        ret_val = api.watcher.ActionPlan.get(self.request, action_plan_id)
        self.assertIsInstance(ret_val, api.watcher.ActionPlan)

    def test_action_plan_start(self):
        action_plan_id = self.api_action_plans.first()['id']
        patch = []
        patch.append({'path': '/state', 'value': 'TRIGGERED', 'op': 'replace'})

        watcherclient = self.stub_watcherclient()
        watcherclient.action_plan = self.mox.CreateMockAnything()
        watcherclient.action_plan.update(action_plan_id, patch)
        self.mox.ReplayAll()

        api.watcher.ActionPlan.start(self.request, action_plan_id)

    def test_action_plan_delete(self):
        action_plan_id = self.api_action_plans.first()['id']

        watcherclient = self.stub_watcherclient()
        watcherclient.action_plan = self.mox.CreateMockAnything()
        watcherclient.action_plan.delete(
            action_plan_id=action_plan_id)
        self.mox.ReplayAll()

        api.watcher.ActionPlan.delete(self.request, action_plan_id)

    def test_action_list(self):
        actions = {'actions': self.api_actions.list()}
        watcherclient = self.stub_watcherclient()

        watcherclient.action = self.mox.CreateMockAnything()
        watcherclient.action.list(
            action_plan=None, detail=True).AndReturn(actions)
        self.mox.ReplayAll()

        ret_val = api.watcher.Action.list(
            self.request,
            action_plan_filter=None)
        for n in ret_val:
            self.assertIsInstance(n, api.watcher.Action)
