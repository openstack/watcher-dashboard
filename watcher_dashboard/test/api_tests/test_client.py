# Copyright 2025,  Red Hat, Inc.
# All rights reserved.

# Licensed under the Apache License, Version 2.0 (the "License"); you may
# not use this file except in compliance with the License. You may obtain
# a copy of the License at
#
#      http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS, WITHOUT
# WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the
# License for the specific language governing permissions and limitations
# under the License.

from unittest import mock

from watcher_dashboard import api
from watcher_dashboard.test import helpers as test


class WatcherClientAPITests(test.APITestCase):

    def test_audit_create_uses_1_1_when_start_end_present(self):
        watcherclient = self.stub_watcherclient()
        watcherclient.audit.create = mock.Mock(return_value={})

        with mock.patch('watcher_dashboard.api.watcher.watcherclient') as wc:
            client_mock = mock.Mock()
            wc.return_value = client_mock
            client_mock.audit.create = mock.Mock(return_value={})

            api.watcher.Audit.create(self.request,
                                     audit_template_uuid='tpl',
                                     audit_type='continuous',
                                     name='n',
                                     interval='60',
                                     start_time='2025-01-01T10:00:00',
                                     end_time='2025-01-01T11:00:00')

            wc.assert_called_with(self.request, api_version='1.1')
            client_mock.audit.create.assert_called_once()

    def test_audit_create_uses_1_1_even_without_start_end(self):
        with mock.patch('watcher_dashboard.api.watcher.watcherclient') as wc:
            client_mock = mock.Mock()
            wc.return_value = client_mock
            client_mock.audit.create = mock.Mock(return_value={})

            api.watcher.Audit.create(self.request,
                                     audit_template_uuid='tpl',
                                     audit_type='continuous',
                                     name='n',
                                     interval='60')

            wc.assert_called_with(self.request, api_version='1.1')
            client_mock.audit.create.assert_called_once()
