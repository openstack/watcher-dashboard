# Copyright 2012 United States Government as represented by the
# Administrator of the National Aeronautics and Space Administration.
# All Rights Reserved.
#
# Copyright 2012 Nebula, Inc.
#
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

from unittest import mock

from openstack_dashboard.test import helpers

from watcher_dashboard import api
from watcher_dashboard.test.test_data import utils


class WatcherTestsMixin:
    def _setup_test_data(self):
        super()._setup_test_data()
        utils.load_test_data(self)


class TestCase(WatcherTestsMixin, helpers.TestCase):
    pass


class APITestCase(WatcherTestsMixin, helpers.APITestCase):
    def setUp(self):
        super().setUp()

        self._original_watcherclient = api.watcher.watcherclient

        api.watcher.watcherclient = (
            lambda request, *args, **kwargs: self.stub_watcherclient())

    def tearDown(self):
        super().tearDown()
        api.watcher.watcherclient = self._original_watcherclient

    def stub_watcherclient(self):
        if not hasattr(self, "watcherclient"):
            self.watcherclient = mock.Mock()
        return self.watcherclient


class BaseAdminViewTests(WatcherTestsMixin, helpers.BaseAdminViewTests):
    pass
