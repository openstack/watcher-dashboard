#    Licensed under the Apache License, Version 2.0 (the "License"); you may
#    not use this file except in compliance with the License. You may obtain
#    a copy of the License at
#
#         http://www.apache.org/licenses/LICENSE-2.0
#
#    Unless required by applicable law or agreed to in writing, software
#    distributed under the License is distributed on an "AS IS" BASIS, WITHOUT
#    WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the
#    License for the specific language governing permissions and limitations
#    under the License.


import copy

from watcher_dashboard.api import watcher
from watcher_dashboard.test.test_data import utils


def data(TEST):

    TEST.service_catalog.append(
        {"type": "infra-optim",
         "name": "watcher",
         "endpoints_links": [],
         "endpoints": [
             {"region": "RegionOne",
              "adminURL": "http://admin.watcher.example.com:9322",
              "internalURL": "http://int.watcher.example.com:9322",
              "publicURL": "http://public.watcher.example.com:9322"},
             {"region": "RegionTwo",
              "adminURL": "http://admin.watcher2.example.com:9322",
              "internalURL": "http://int.watcher2.example.com:9322",
              "publicURL": "http://public.watcher2.example.com:9322"}]},
    )

    TEST.goals = utils.TestDataContainer()
    TEST.efficacy_specifications = utils.TestDataContainer()
    TEST.api_goals = utils.TestDataContainer()
    efficacy_specifications_dict1 = {'name': 'spec1'}
    efficacy_specifications_dict2 = {'name': 'spec2'}
    spec1 = watcher.EfficacyIndicatorSpec(efficacy_specifications_dict1)
    spec2 = watcher.EfficacyIndicatorSpec(efficacy_specifications_dict2)
    goal_dict1 = {
        'uuid': 'gggggggg-1111-1111-1111-gggggggggggg',
        'name': 'MINIMIZE_LICENSING_COST',
        'display_name': 'Dummy',
        'efficacy_specifications': spec1
    }
    goal_dict2 = {
        'uuid': 'gggggggg-2222-2222-2222-gggggggggggg',
        'name': 'SERVER_CONSOLIDATION',
        'display_name': 'Server consolidation',
        'efficacy_specifications': spec2
    }
    TEST.api_goals.add(goal_dict1)
    TEST.api_goals.add(goal_dict2)
    _goal_dict1 = copy.deepcopy(goal_dict1)
    _goal_dict2 = copy.deepcopy(goal_dict2)

    TEST.strategies = utils.TestDataContainer()
    TEST.api_strategies = utils.TestDataContainer()
    strategy_dict1 = {
        'uuid': 'ssssssss-1111-1111-1111-ssssssssssss',
        'name': 'minimize_licensing_cost1',
        'goal_uuid': 'gggggggg-1111-1111-1111-gggggggggggg',
        'display_name': 'Fake licensing cost strategy1',
    }
    strategy_dict2 = {
        'uuid': 'ssssssss-2222-2222-2222-ssssssssssss',
        'name': 'minimize_licensing_cost2',
        'goal_uuid': 'gggggggg-1111-1111-1111-gggggggggggg',
        'display_name': 'Fake licensing cost strategy2',
    }
    strategy_dict3 = {
        'uuid': 'ssssssss-3333-3333-3333-ssssssssssss',
        'name': 'sercon',
        'goal_uuid': 'gggggggg-2222-2222-2222-gggggggggggg',
        'display_name': 'Fake Sercon',
    }
    TEST.api_strategies.add(strategy_dict1)
    TEST.api_strategies.add(strategy_dict2)
    TEST.api_strategies.add(strategy_dict3)
    _strategy_dict1 = copy.deepcopy(strategy_dict1)
    _strategy_dict2 = copy.deepcopy(strategy_dict2)
    _strategy_dict3 = copy.deepcopy(strategy_dict3)

    TEST.audit_templates = utils.TestDataContainer()
    TEST.api_audit_templates = utils.TestDataContainer()
    audit_template_dict = {
        'uuid': '11111111-1111-1111-1111-111111111111',
        'name': 'Audit Template 1',
        'description': 'Audit Template 1 description',
        'scope': '',
        'goal_uuid': 'gggggggg-1111-1111-1111-gggggggggggg',
        'strategy_uuid': 'ssssssss-1111-1111-1111-ssssssssssss',
    }
    audit_template_dict2 = {
        'uuid': '11111111-2222-2222-2222-111111111111',
        'name': 'Audit Template 2',
        'description': 'Audit Template 2 description',
        'scope': '',
        'goal_uuid': 'gggggggg-1111-1111-1111-gggggggggggg',
        'strategy_uuid': 'ssssssss-2222-2222-2222-ssssssssssss',
    }
    audit_template_dict3 = {
        'uuid': '11111111-3333-3333-3333-111111111111',
        'name': 'Audit Template 1',
        'description': 'Audit Template 3 description',
        'scope': '',
        'goal_uuid': 'gggggggg-2222-2222-2222-gggggggggggg',
        'strategy_uuid': None,
    }
    TEST.api_audit_templates.add(audit_template_dict)
    TEST.api_audit_templates.add(audit_template_dict2)
    TEST.api_audit_templates.add(audit_template_dict3)
    _audit_template_dict = copy.deepcopy(audit_template_dict)
    _audit_template_dict2 = copy.deepcopy(audit_template_dict2)
    _audit_template_dict3 = copy.deepcopy(audit_template_dict3)

    TEST.audits = utils.TestDataContainer()
    TEST.api_audits = utils.TestDataContainer()
    audit_dict = {
        'uuid': '22222222-2222-2222-2222-222222222222',
        'audit_type': 'ONESHOT',
        'name': 'Audit 1',
        'audit_template_uuid': '11111111-1111-1111-1111-111111111111',
        'interval': None,
    }
    audit_dict2 = {
        'uuid': '33333333-3333-3333-3333-333333333333',
        'audit_type': 'CONTINUOUS',
        'name': 'Audit 2',
        'audit_template_uuid': '11111111-1111-1111-1111-111111111111',
        'interval': 60,
    }
    TEST.api_audits.add(audit_dict)
    TEST.api_audits.add(audit_dict2)
    _audit_dict = copy.deepcopy(audit_dict)

    TEST.action_plans = utils.TestDataContainer()
    TEST.api_action_plans = utils.TestDataContainer()
    action_plan_dict = {
        'uuid': '33333333-3333-3333-3333-333333333333',
        'state': 'RECOMMENDED',
        'first_action_uuid': '44444444-4444-4444-4444-111111111111',
        'audit_uuid': '33333333-3333-3333-3333-333333333333'
    }
    TEST.api_action_plans.add(action_plan_dict)
    _action_plan_dict = copy.deepcopy(action_plan_dict)

    TEST.actions = utils.TestDataContainer()
    TEST.api_actions = utils.TestDataContainer()
    action_dict1 = {
        'uuid': '44444444-4444-4444-4444-111111111111',
        'state': 'PENDING',
        'next_uuid': '44444444-4444-4444-4444-222222222222',
        'action_plan_uuid': '33333333-3333-3333-3333-333333333333'
    }
    TEST.api_actions.add(action_dict1)

    action_dict2 = {
        'uuid': '44444444-4444-4444-4444-222222222222',
        'state': 'PENDING',
        'next_uuid': None,
        'action_plan_uuid': '33333333-3333-3333-3333-333333333333'
    }
    TEST.api_actions.add(action_dict2)

    action2 = watcher.Action(action_dict2)
    action1 = watcher.Action(action_dict1)
    TEST.actions.add(action1)
    TEST.actions.add(action2)

    _action_plan_dict['actions'] = [action1, action2]
    action_plan = watcher.ActionPlan(_action_plan_dict)

    _audit_dict['action_plans'] = [action_plan]
    audit = watcher.Audit(_audit_dict)

    goal1 = watcher.Goal(_goal_dict1)
    goal2 = watcher.Goal(_goal_dict2)

    strategy1 = watcher.Strategy(_strategy_dict1)
    strategy2 = watcher.Strategy(_strategy_dict2)
    strategy3 = watcher.Strategy(_strategy_dict3)

    audit_template1 = watcher.AuditTemplate(_audit_template_dict)
    audit_template2 = watcher.AuditTemplate(_audit_template_dict2)
    audit_template3 = watcher.AuditTemplate(_audit_template_dict3)

    TEST.goals.add(goal1)
    TEST.goals.add(goal2)
    TEST.strategies.add(strategy1)
    TEST.strategies.add(strategy2)
    TEST.strategies.add(strategy3)

    TEST.audit_templates.add(audit_template1)
    TEST.audit_templates.add(audit_template2)
    TEST.audit_templates.add(audit_template3)
    TEST.audits.add(audit)
    TEST.action_plans.add(watcher.ActionPlan(action_plan))
