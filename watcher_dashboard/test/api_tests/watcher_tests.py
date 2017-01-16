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

    def test_goal_list(self):
        goals = {'goals': self.api_goals.list()}
        watcherclient = self.stub_watcherclient()

        watcherclient.goal = self.mox.CreateMockAnything()
        watcherclient.goal.list(detail=True).AndReturn(goals)
        self.mox.ReplayAll()

        ret_val = api.watcher.Goal.list(self.request)
        self.assertIsInstance(ret_val, dict)
        self.assertIn('goals', ret_val)
        for n in ret_val['goals']:
            self.assertIsInstance(n, dict)

    def test_goal_get(self):
        goal = self.api_goals.first()
        goal_id = self.api_goals.first()['uuid']

        watcherclient = self.stub_watcherclient()
        watcherclient.goal = self.mox.CreateMockAnything()
        watcherclient.goal.get(goal_id).AndReturn(goal)
        self.mox.ReplayAll()

        ret_val = api.watcher.Goal.get(self.request, goal_id)
        self.assertIsInstance(ret_val, dict)

    def test_strategy_list(self):
        strategies = {'strategies': self.api_strategies.list()}
        watcherclient = self.stub_watcherclient()

        watcherclient.strategy = self.mox.CreateMockAnything()
        watcherclient.strategy.list(detail=True).AndReturn(strategies)
        self.mox.ReplayAll()

        ret_val = api.watcher.Strategy.list(self.request)
        self.assertIn('strategies', ret_val)
        for n in ret_val['strategies']:
            self.assertIsInstance(n, dict)

    def test_strategy_get(self):
        strategy = self.api_strategies.first()
        strategy_id = self.api_strategies.first()['uuid']

        watcherclient = self.stub_watcherclient()
        watcherclient.strategy = self.mox.CreateMockAnything()
        watcherclient.strategy.get(strategy_id).AndReturn(strategy)
        self.mox.ReplayAll()

        ret_val = api.watcher.Strategy.get(self.request, strategy_id)
        self.assertIsInstance(ret_val, dict)

    def test_audit_template_list(self):
        audit_templates = {
            'audit_templates': self.api_audit_templates.list()}
        watcherclient = self.stub_watcherclient()

        watcherclient.audit_template = self.mox.CreateMockAnything()
        watcherclient.audit_template.list(
            detail=True).AndReturn(audit_templates)
        self.mox.ReplayAll()

        ret_val = api.watcher.AuditTemplate.list(self.request)

        self.assertIn('audit_templates', ret_val)
        for n in ret_val['audit_templates']:
            self.assertIsInstance(n, dict)

    def test_audit_template_list_with_filters(self):
        search_opts = {'name': 'Audit Template 1'}
        audit_templates = {
            'audit_templates': self.api_audit_templates.filter(**search_opts)}
        watcherclient = self.stub_watcherclient()

        watcherclient.audit_template = self.mox.CreateMockAnything()

        watcherclient.audit_template.list(
            detail=True, **search_opts).AndReturn(audit_templates)
        self.mox.ReplayAll()

        ret_val = api.watcher.AuditTemplate.list(
            self.request, **search_opts)

        self.assertIn('audit_templates', ret_val)
        for n in ret_val['audit_templates']:
            self.assertIsInstance(n, dict)

        self.assertEqual(ret_val, audit_templates)

    def test_audit_template_get(self):
        audit_template = self.api_audit_templates.first()
        audit_template_id = self.api_audit_templates.first()['uuid']

        watcherclient = self.stub_watcherclient()
        watcherclient.audit_template = self.mox.CreateMockAnything()
        watcherclient.audit_template.get(
            audit_template_id=audit_template_id).AndReturn(audit_template)
        self.mox.ReplayAll()

        ret_val = api.watcher.AuditTemplate.get(self.request,
                                                audit_template_id)
        self.assertIsInstance(ret_val, dict)

    def test_audit_template_create(self):
        audit_template = self.api_audit_templates.first()
        name = audit_template['name']
        goal = audit_template['goal_uuid']
        strategy = audit_template['strategy_uuid']
        description = audit_template['description']
        scope = audit_template['scope']

        watcherclient = self.stub_watcherclient()
        watcherclient.audit_template = self.mox.CreateMockAnything()
        watcherclient.audit_template.create(
            name=name,
            goal=goal,
            strategy=strategy,
            description=description,
            scope=scope).AndReturn(audit_template)
        self.mox.ReplayAll()

        ret_val = api.watcher.AuditTemplate.create(
            self.request, name, goal, strategy,
            description, scope)
        self.assertIsInstance(ret_val, dict)

    def test_audit_template_patch(self):
        audit_template = self.api_audit_templates.first()
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
        self.assertIsInstance(ret_val, dict)

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
        watcherclient.audit.list(detail=True).AndReturn(audits)
        self.mox.ReplayAll()

        ret_val = api.watcher.Audit.list(self.request)

        self.assertIn('audits', ret_val)
        for n in ret_val['audits']:
            self.assertIsInstance(n, dict)

    def test_audit_get(self):
        audit = self.api_audits.first()
        audit_id = self.api_audits.first()['uuid']

        watcherclient = self.stub_watcherclient()
        watcherclient.audit = self.mox.CreateMockAnything()
        watcherclient.audit.get(audit_id=audit_id).AndReturn(audit)
        self.mox.ReplayAll()

        ret_val = api.watcher.Audit.get(self.request, audit_id)
        self.assertIsInstance(ret_val, dict)

    def test_audit_create(self):
        audit = self.api_audits.first()
        audit_template_id = self.api_audit_templates.first()['uuid']

        audit_type = self.api_audits.first()['audit_type']
        audit_template_uuid = audit_template_id

        watcherclient = self.stub_watcherclient()
        watcherclient.audit = self.mox.CreateMockAnything()
        watcherclient.audit.create(
            audit_template_uuid=audit_template_uuid,
            audit_type=audit_type, auto_trigger=False).AndReturn(audit)
        self.mox.ReplayAll()

        ret_val = api.watcher.Audit.create(
            self.request, audit_template_uuid, audit_type)
        self.assertIsInstance(ret_val, dict)

    def test_audit_create_with_interval(self):
        audit = self.api_audits.list()[1]
        audit_template_id = self.api_audit_templates.first()['uuid']

        audit_type = self.api_audits.first()['audit_type']
        interval = audit['interval']
        audit_template_uuid = audit_template_id

        watcherclient = self.stub_watcherclient()
        watcherclient.audit = self.mox.CreateMockAnything()
        watcherclient.audit.create(
            audit_template_uuid=audit_template_uuid,
            audit_type=audit_type,
            auto_trigger=False,
            interval=interval).AndReturn(audit)
        self.mox.ReplayAll()

        ret_val = api.watcher.Audit.create(
            self.request, audit_template_uuid, audit_type, False, interval)
        self.assertIsInstance(ret_val, dict)

    def test_audit_create_with_auto_trigger(self):
        audit = self.api_audits.list()[1]
        audit_template_id = self.api_audit_templates.first()['uuid']

        audit_type = self.api_audits.first()['audit_type']
        audit_template_uuid = audit_template_id

        watcherclient = self.stub_watcherclient()
        watcherclient.audit = self.mox.CreateMockAnything()
        watcherclient.audit.create(
            audit_template_uuid=audit_template_uuid,
            audit_type=audit_type,
            auto_trigger=True).AndReturn(audit)
        self.mox.ReplayAll()

        ret_val = api.watcher.Audit.create(
            self.request, audit_template_uuid, audit_type, True)
        self.assertIsInstance(ret_val, dict)

    def test_audit_delete(self):
        audit_id = self.api_audits.first()['uuid']

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
        watcherclient.action_plan.list(detail=True).AndReturn(action_plans)
        self.mox.ReplayAll()

        ret_val = api.watcher.ActionPlan.list(self.request)

        self.assertIn('action_plans', ret_val)
        for n in ret_val['action_plans']:
            self.assertIsInstance(n, dict)

    def test_action_plan_get(self):
        action_plan = self.api_action_plans.first()
        action_plan_id = self.api_action_plans.first()['uuid']

        watcherclient = self.stub_watcherclient()
        watcherclient.action_plan = self.mox.CreateMockAnything()
        watcherclient.action_plan.get(
            action_plan_id=action_plan_id).AndReturn(action_plan)
        self.mox.ReplayAll()

        ret_val = api.watcher.ActionPlan.get(self.request, action_plan_id)
        self.assertIsInstance(ret_val, dict)

    def test_action_plan_start(self):
        action_plan_id = self.api_action_plans.first()['uuid']

        watcherclient = self.stub_watcherclient()
        watcherclient.action_plan = self.mox.CreateMockAnything()
        watcherclient.action_plan.start(action_plan_id)
        self.mox.ReplayAll()

        api.watcher.ActionPlan.start(self.request, action_plan_id)

    def test_action_plan_delete(self):
        action_plan_id = self.api_action_plans.first()['uuid']

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
        watcherclient.action.list(detail=True).AndReturn(actions)
        self.mox.ReplayAll()

        ret_val = api.watcher.Action.list(self.request)

        self.assertIn('actions', ret_val)
        for n in ret_val['actions']:
            self.assertIsInstance(n, dict)
