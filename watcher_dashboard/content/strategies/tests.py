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
    'horizon:admin:strategies:index')
DETAILS_VIEW = 'horizon:admin:strategies:detail'


class StrategiesTest(test.BaseAdminViewTests):

    goal_list = [
        'BASIC_CONSOLIDATION',
        'MINIMIZE_ENERGY_CONSUMPTION',
        'BALANCE_LOAD',
        'MINIMIZE_LICENSING_COST',
        'PREPARED_PLAN_OPERATION',
    ]

    @mock.patch.object(api.watcher.Strategy, 'list')
    def test_index(self, mock_list):
        mock_list.return_value = self.strategies.list()

        res = self.client.get(INDEX_URL)
        self.assertTemplateUsed(res, 'infra_optim/strategies/index.html')
        strategies = res.context['strategies_table'].data
        self.assertCountEqual(strategies, self.strategies.list())

    @mock.patch.object(api.watcher.Strategy, 'list')
    def test_strategy_list_unavailable(self, mock_list):
        mock_list.side_effect = self.exceptions.watcher

        resp = self.client.get(INDEX_URL)
        self.assertMessageCount(resp, error=1, warning=0)

    @mock.patch.object(api.watcher.Strategy, 'get')
    def test_details(self, mock_get):
        at = self.strategies.first()
        at_id = at.uuid
        mock_get.return_value = at

        DETAILS_URL = urls.reverse(DETAILS_VIEW, args=[at_id])
        res = self.client.get(DETAILS_URL)
        self.assertTemplateUsed(res,
                                'infra_optim/strategies/details.html')
        strategies = res.context['strategy']
        self.assertCountEqual([strategies], [at])

    @mock.patch.object(api.watcher.Strategy, 'get')
    def test_details_exception(self, mock_get):
        at = self.strategies.first()
        at_id = at.uuid
        mock_get.side_effect = self.exceptions.watcher

        DETAILS_URL = urls.reverse(DETAILS_VIEW, args=[at_id])
        res = self.client.get(DETAILS_URL)
        self.assertRedirectsNoFollow(res, INDEX_URL)
