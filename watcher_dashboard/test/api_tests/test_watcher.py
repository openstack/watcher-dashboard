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

from watcher_dashboard import api
from watcher_dashboard.test import helpers as test


class WatcherAPITests(test.APITestCase):

    def test_goal_list(self):
        goals = {'goals': self.api_goals.list()}
        watcherclient = self.stub_watcherclient()
        watcherclient.goal.list = mock.Mock(
            return_value=goals)

        ret_val = api.watcher.Goal.list(self.request)
        self.assertIsInstance(ret_val, dict)
        self.assertIn('goals', ret_val)
        for n in ret_val['goals']:
            self.assertIsInstance(n, dict)
        watcherclient.goal.list.assert_called_with(
            detail=True)

    def test_goal_get(self):
        goal = self.api_goals.first()
        goal_id = self.api_goals.first()['uuid']

        watcherclient = self.stub_watcherclient()
        watcherclient.goal.get = mock.Mock(
            return_value=goal)

        ret_val = api.watcher.Goal.get(self.request, goal_id)
        self.assertIsInstance(ret_val, dict)
        watcherclient.goal.get.assert_called_with(
            goal_id)

    def test_strategy_list(self):
        strategies = {'strategies': self.api_strategies.list()}
        watcherclient = self.stub_watcherclient()

        watcherclient.strategy.list = mock.Mock(
            return_value=strategies)

        ret_val = api.watcher.Strategy.list(self.request)
        self.assertIn('strategies', ret_val)
        for n in ret_val['strategies']:
            self.assertIsInstance(n, dict)
        watcherclient.strategy.list.assert_called_with(
            detail=True)

    def test_strategy_get(self):
        strategy = self.api_strategies.first()
        strategy_id = self.api_strategies.first()['uuid']

        watcherclient = self.stub_watcherclient()
        watcherclient.strategy.get = mock.Mock(
            return_value=strategy)

        ret_val = api.watcher.Strategy.get(self.request, strategy_id)
        self.assertIsInstance(ret_val, dict)
        watcherclient.strategy.get.assert_called_with(
            strategy_id)

    def test_audit_template_list(self):
        audit_templates = {
            'audit_templates': self.api_audit_templates.list()}
        watcherclient = self.stub_watcherclient()

        watcherclient.audit_template.list = mock.Mock(
            return_value=audit_templates)

        ret_val = api.watcher.AuditTemplate.list(self.request)

        self.assertIn('audit_templates', ret_val)
        for n in ret_val['audit_templates']:
            self.assertIsInstance(n, dict)
        watcherclient.audit_template.list.assert_called_with(
            detail=True)

    def test_audit_template_list_with_filters(self):
        search_opts = {'name': 'Audit Template 1'}
        audit_templates = {
            'audit_templates': self.api_audit_templates.filter(**search_opts)}
        watcherclient = self.stub_watcherclient()

        watcherclient.audit_template.list = mock.Mock(
            return_value=audit_templates)

        ret_val = api.watcher.AuditTemplate.list(
            self.request, **search_opts)

        self.assertIn('audit_templates', ret_val)
        for n in ret_val['audit_templates']:
            self.assertIsInstance(n, dict)

        self.assertEqual(ret_val, audit_templates)
        watcherclient.audit_template.list.assert_called_with(
            detail=True, **search_opts)

    def test_audit_template_get(self):
        audit_template = self.api_audit_templates.first()
        audit_template_id = self.api_audit_templates.first()['uuid']

        watcherclient = self.stub_watcherclient()
        watcherclient.audit_template.get = mock.Mock(
            return_value=audit_template)

        ret_val = api.watcher.AuditTemplate.get(self.request,
                                                audit_template_id)
        self.assertIsInstance(ret_val, dict)
        watcherclient.audit_template.get.assert_called_with(
            audit_template_id=audit_template_id)

    def test_audit_template_create(self):
        audit_template = self.api_audit_templates.first()
        name = audit_template['name']
        goal = audit_template['goal_uuid']
        strategy = audit_template['strategy_uuid']
        description = audit_template['description']
        scope = audit_template['scope']

        watcherclient = self.stub_watcherclient()
        watcherclient.audit_template.create = mock.Mock(
            return_value=audit_template)

        ret_val = api.watcher.AuditTemplate.create(
            self.request, name, goal, strategy,
            description, scope)
        self.assertIsInstance(ret_val, dict)
        watcherclient.audit_template.create.assert_called_with(
            name=name,
            goal=goal,
            strategy=strategy,
            description=description,
            scope=scope)

    def test_audit_template_patch(self):
        audit_template = self.api_audit_templates.first()
        audit_template_id = self.api_audit_templates.first()['uuid']
        form_data = {'name': 'new Audit Template 1'}

        watcherclient = self.stub_watcherclient()
        watcherclient.audit_template.patch = mock.Mock(
            return_value=audit_template)

        ret_val = api.watcher.AuditTemplate.patch(
            self.request, audit_template_id,
            form_data)
        self.assertIsInstance(ret_val, dict)
        watcherclient.audit_template.patch.assert_called_with(
            audit_template_id,
            [{'name': 'name', 'value': 'new Audit Template 1'}]
        )

    def test_audit_template_delete(self):
        audit_template_list = self.api_audit_templates.list()
        audit_template_id = self.api_audit_templates.first()['uuid']
        deleted_at_list = self.api_audit_templates.delete()

        watcherclient = self.stub_watcherclient()
        watcherclient.audit_template.delete = mock.Mock()
        api.watcher.AuditTemplate.delete(self.request,
                                         audit_template_id)
        self.assertEqual(audit_template_list, deleted_at_list)
        self.assertEqual(len(audit_template_list), len(deleted_at_list))
        watcherclient.audit_template.delete.assert_called_with(
            audit_template_id=audit_template_id)

    def test_audit_list(self):
        audits = {'audits': self.api_audits.list()}

        watcherclient = self.stub_watcherclient()

        watcherclient.audit.list = mock.Mock(
            return_value=audits)

        ret_val = api.watcher.Audit.list(self.request)

        self.assertIn('audits', ret_val)
        for n in ret_val['audits']:
            self.assertIsInstance(n, dict)
        watcherclient.audit.list.assert_called_with(
            detail=True)

    def test_audit_get(self):
        audit = self.api_audits.first()
        audit_id = self.api_audits.first()['uuid']

        watcherclient = self.stub_watcherclient()
        watcherclient.audit.get = mock.Mock(
            return_value=audit)

        ret_val = api.watcher.Audit.get(self.request, audit_id)
        self.assertIsInstance(ret_val, dict)
        watcherclient.audit.get.assert_called_with(
            audit=audit_id)

    def test_audit_create(self):
        audit = self.api_audits.first()
        audit_template_id = self.api_audit_templates.first()['uuid']

        audit_type = self.api_audits.first()['audit_type']
        audit_name = self.api_audits.first()['name']
        audit_template_uuid = audit_template_id

        watcherclient = self.stub_watcherclient()
        watcherclient.audit.create = mock.Mock(
            return_value=audit)

        ret_val = api.watcher.Audit.create(
            self.request, audit_template_uuid, audit_type, audit_name)
        self.assertIsInstance(ret_val, dict)
        watcherclient.audit.create.assert_called_with(
            audit_template_uuid=audit_template_uuid,
            audit_type=audit_type, auto_trigger=False, name=audit_name)

    def test_audit_create_with_interval(self):
        audit = self.api_audits.list()[1]
        audit_template_id = self.api_audit_templates.first()['uuid']

        audit_type = self.api_audits.first()['audit_type']
        audit_name = self.api_audits.first()['name']
        interval = audit['interval']
        audit_template_uuid = audit_template_id

        watcherclient = self.stub_watcherclient()
        watcherclient.audit.create = mock.Mock(
            return_value=audit)

        ret_val = api.watcher.Audit.create(
            self.request, audit_template_uuid, audit_type, audit_name,
            False, interval)
        self.assertIsInstance(ret_val, dict)
        watcherclient.audit.create.assert_called_with(
            audit_template_uuid=audit_template_uuid,
            audit_type=audit_type,
            auto_trigger=False,
            interval=interval,
            name=audit_name)

    def test_audit_create_with_auto_trigger(self):
        audit = self.api_audits.list()[1]
        audit_template_id = self.api_audit_templates.first()['uuid']

        audit_type = self.api_audits.first()['audit_type']
        audit_name = self.api_audits.first()['name']
        audit_template_uuid = audit_template_id

        watcherclient = self.stub_watcherclient()
        watcherclient.audit.create = mock.Mock(
            return_value=audit)

        ret_val = api.watcher.Audit.create(
            self.request, audit_template_uuid, audit_type, audit_name, True)
        self.assertIsInstance(ret_val, dict)
        watcherclient.audit.create.assert_called_with(
            audit_template_uuid=audit_template_uuid,
            audit_type=audit_type,
            auto_trigger=True,
            name=audit_name)

    def test_audit_delete(self):
        audit_id = self.api_audits.first()['uuid']

        watcherclient = self.stub_watcherclient()
        watcherclient.audit.delete = mock.Mock()

        api.watcher.Audit.delete(self.request, audit_id)
        watcherclient.audit.delete.assert_called_with(
            audit=audit_id)

    def test_action_plan_list(self):
        action_plans = {'action_plans': self.api_action_plans.list()}

        watcherclient = self.stub_watcherclient()

        watcherclient.action_plan.list = mock.Mock(
            return_value=action_plans)

        ret_val = api.watcher.ActionPlan.list(self.request)

        self.assertIn('action_plans', ret_val)
        for n in ret_val['action_plans']:
            self.assertIsInstance(n, dict)
        watcherclient.action_plan.list.assert_called_with(
            detail=True)

    def test_action_plan_get(self):
        action_plan = self.api_action_plans.first()
        action_plan_id = self.api_action_plans.first()['uuid']

        watcherclient = self.stub_watcherclient()
        watcherclient.action_plan.get = mock.Mock(
            return_value=action_plan)

        ret_val = api.watcher.ActionPlan.get(self.request, action_plan_id)
        self.assertIsInstance(ret_val, dict)
        watcherclient.action_plan.get.assert_called_with(
            action_plan_id=action_plan_id)

    def test_action_plan_start(self):
        action_plan_id = self.api_action_plans.first()['uuid']

        watcherclient = self.stub_watcherclient()
        watcherclient.action_plan.start = mock.Mock()

        api.watcher.ActionPlan.start(self.request, action_plan_id)
        watcherclient.action_plan.start.assert_called_with(
            action_plan_id)

    def test_action_plan_delete(self):
        action_plan_id = self.api_action_plans.first()['uuid']

        watcherclient = self.stub_watcherclient()
        watcherclient.action_plan.delete = mock.Mock()

        api.watcher.ActionPlan.delete(self.request, action_plan_id)
        watcherclient.action_plan.delete.assert_called_with(
            action_plan_id=action_plan_id)

    def test_action_list(self):
        actions = {'actions': self.api_actions.list()}
        watcherclient = self.stub_watcherclient()

        watcherclient.action.list = mock.Mock(
            return_value=actions)

        ret_val = api.watcher.Action.list(self.request)

        self.assertIn('actions', ret_val)
        for n in ret_val['actions']:
            self.assertIsInstance(n, dict)
        watcherclient.action.list.assert_called_with(
            detail=True)
