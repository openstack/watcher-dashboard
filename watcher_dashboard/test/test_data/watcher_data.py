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

    TEST.audit_templates = utils.TestDataContainer()
    TEST.api_audit_templates = utils.TestDataContainer()
    audit_template_dict = {
        'uuid': '11111111-1111-1111-1111-111111111111',
        'name': 'Audit Template 1',
        'description': 'Audit Template 1 description',
        'host_aggregate': None,
        'extra': {'automatic': False},
        'goal': 'MINIMIZE_LICENSING_COST'
    }
    audit_template_dict2 = {
        'uuid': '11111111-2222-2222-2222-111111111111',
        'name': 'Audit Template 2',
        'description': 'Audit Template 2 description',
        'host_aggregate': None,
        'extra': {'automatic': False},
        'goal': 'MINIMIZE_LICENSING_COST'
    }
    audit_template_dict3 = {
        'uuid': '11111111-3333-3333-3333-111111111111',
        'name': 'Audit Template 1',
        'description': 'Audit Template 3 description',
        'host_aggregate': None,
        'extra': {'automatic': False},
        'goal': 'MINIMIZE_LICENSING_COST'
    }
    TEST.api_audit_templates.add(audit_template_dict)
    TEST.api_audit_templates.add(audit_template_dict2)
    TEST.api_audit_templates.add(audit_template_dict3)
    _audit_template_dict = copy.deepcopy(audit_template_dict)
    _audit_template_dict2 = copy.deepcopy(audit_template_dict2)
    _audit_template_dict3 = copy.deepcopy(audit_template_dict3)

    TEST.goals = utils.TestDataContainer()
    TEST.api_goals = utils.TestDataContainer()

    TEST.audits = utils.TestDataContainer()
    TEST.api_audits = utils.TestDataContainer()
    audit_dict = {
        'id': '22222222-2222-2222-2222-222222222222',
        'deadline': None,
        'type': 'ONE_SHOT',
        'audit_template_uuid': '11111111-1111-1111-1111-111111111111'
    }
    TEST.api_audits.add(audit_dict)
    _audit_dict = copy.deepcopy(audit_dict)

    TEST.action_plans = utils.TestDataContainer()
    TEST.api_action_plans = utils.TestDataContainer()
    action_plan_dict = {
        'id': '33333333-3333-3333-3333-333333333333',
        'state': 'RECOMMENDED',
        'first_action_uuid': '44444444-4444-4444-4444-111111111111',
        'audit_uuid': '22222222-2222-2222-2222-222222222222'
    }
    TEST.api_action_plans.add(action_plan_dict)
    _action_plan_dict = copy.deepcopy(action_plan_dict)

    TEST.actions = utils.TestDataContainer()
    TEST.api_actions = utils.TestDataContainer()
    action_dict1 = {
        'id': '44444444-4444-4444-4444-111111111111',
        'state': 'PENDING',
        'next_uuid': '44444444-4444-4444-4444-222222222222',
        'action_plan_uuid': '33333333-3333-3333-3333-333333333333'
    }
    TEST.api_actions.add(action_dict1)

    action_dict2 = {
        'id': '44444444-4444-4444-4444-222222222222',
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

    # _audit_template_dict['audits'] = [audit]
    audit_template1 = watcher.AuditTemplate(_audit_template_dict)
    audit_template2 = watcher.AuditTemplate(_audit_template_dict2)
    audit_template3 = watcher.AuditTemplate(_audit_template_dict3)

    TEST.audit_templates.add(audit_template1)
    TEST.audit_templates.add(audit_template2)
    TEST.audit_templates.add(audit_template3)
    TEST.audits.add(audit)
    TEST.action_plans.add(watcher.ActionPlan(action_plan))
