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

    @test.create_stubs({api.watcher.Strategy: ('list',)})
    def test_index(self):
        search_opts = {}
        api.watcher.Strategy.list(
            IsA(http.HttpRequest), **search_opts
        ).MultipleTimes().AndReturn(self.strategies.list())
        self.mox.ReplayAll()

        res = self.client.get(INDEX_URL)
        self.assertTemplateUsed(res, 'infra_optim/strategies/index.html')
        strategies = res.context['strategies_table'].data
        self.assertItemsEqual(strategies, self.strategies.list())

    @test.create_stubs({api.watcher.Strategy: ('list',)})
    def test_strategy_list_unavailable(self):
        search_opts = {}
        api.watcher.Strategy.list(
            IsA(http.HttpRequest), **search_opts).MultipleTimes().AndRaise(
            self.exceptions.watcher)
        self.mox.ReplayAll()

        resp = self.client.get(INDEX_URL)
        self.assertMessageCount(resp, error=1, warning=0)

    @test.create_stubs({api.watcher.Strategy: ('get',)})
    def test_details(self):
        at = self.strategies.first()
        at_id = at.uuid
        api.watcher.Strategy.get(
            IsA(http.HttpRequest), at_id).\
            MultipleTimes().AndReturn(at)
        self.mox.ReplayAll()
        DETAILS_URL = urlresolvers.reverse(DETAILS_VIEW, args=[at_id])
        res = self.client.get(DETAILS_URL)
        self.assertTemplateUsed(res,
                                'infra_optim/strategies/details.html')
        strategies = res.context['strategy']
        self.assertItemsEqual([strategies], [at])

    @test.create_stubs({api.watcher.Strategy: ('get',)})
    def test_details_exception(self):
        at = self.strategies.first()
        at_id = at.uuid
        api.watcher.Strategy.get(IsA(http.HttpRequest), at_id) \
            .AndRaise(self.exceptions.watcher)

        self.mox.ReplayAll()

        DETAILS_URL = urlresolvers.reverse(DETAILS_VIEW, args=[at_id])
        res = self.client.get(DETAILS_URL)
        self.assertRedirectsNoFollow(res, INDEX_URL)
