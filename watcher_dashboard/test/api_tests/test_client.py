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
from watcher_dashboard.common import client as common_client
from watcher_dashboard.test import helpers as test


class UnitWatcherClientAPITests(test.APITestCase):
    def test_audit_create_defaults_to_min_version(self):
        with mock.patch(
            'watcher_dashboard.api.watcher.watcherclient', autospec=True
        ) as wc:
            client_mock = mock.Mock()
            wc.return_value = client_mock
            client_mock.audit.create = mock.Mock(return_value={})

            api.watcher.Audit.create(
                self.request,
                audit_template_uuid='tpl',
                audit_type='continuous',
                name='n',
                interval='60',
            )

            wc.assert_called_with(self.request, api_version=None)
            client_mock.audit.create.assert_called_once()

    def test_audit_create_passes_explicit_api_version(self):
        with mock.patch(
            'watcher_dashboard.api.watcher.watcherclient', autospec=True
        ) as wc:
            client_mock = mock.Mock()
            wc.return_value = client_mock
            client_mock.audit.create = mock.Mock(return_value={})

            api.watcher.Audit.create(
                self.request,
                audit_template_uuid='tpl',
                audit_type='continuous',
                name='n',
                interval='60',
                start_time='2025-01-01T10:00:00',
                end_time='2025-01-01T11:00:00',
                api_version='1.1',
            )

            wc.assert_called_with(self.request, api_version='1.1')
            client_mock.audit.create.assert_called_once()

    def test_audit_list_passes_explicit_api_version(self):
        with mock.patch(
            'watcher_dashboard.api.watcher.watcherclient', autospec=True
        ) as wc:
            client_mock = mock.Mock()
            wc.return_value = client_mock
            client_mock.audit.list = mock.Mock(return_value=[])

            api.watcher.Audit.list(self.request, api_version='1.1')

            wc.assert_called_with(self.request, api_version='1.1')

    def test_audit_get_passes_explicit_api_version(self):
        with mock.patch(
            'watcher_dashboard.api.watcher.watcherclient', autospec=True
        ) as wc:
            client_mock = mock.Mock()
            wc.return_value = client_mock
            client_mock.audit.get = mock.Mock(return_value={})

            api.watcher.Audit.get(
                self.request, 'audit-uuid', api_version='1.1'
            )

            wc.assert_called_with(self.request, api_version='1.1')

    def test_is_microversion_supported(self):
        self.assertTrue(common_client.is_microversion_supported('1.1', '1.0'))
        self.assertTrue(common_client.is_microversion_supported('1.1', '1.1'))
        self.assertFalse(common_client.is_microversion_supported('1.0', '1.1'))
        self.assertFalse(common_client.is_microversion_supported(None, '1.1'))

    def test_is_microversion_supported_start_end(self):
        self.assertTrue(
            common_client.is_microversion_supported(
                '1.1', common_client.MV_START_END
            )
        )
        self.assertTrue(
            common_client.is_microversion_supported(
                '1.5', common_client.MV_START_END
            )
        )
        self.assertFalse(
            common_client.is_microversion_supported(
                '1.0', common_client.MV_START_END
            )
        )
        self.assertFalse(
            common_client.is_microversion_supported(
                None, common_client.MV_START_END
            )
        )

    def test_is_microversion_supported_skip_action(self):
        self.assertTrue(
            common_client.is_microversion_supported(
                '1.5', common_client.MV_SKIP_ACTION
            )
        )
        self.assertTrue(
            common_client.is_microversion_supported(
                '2.0', common_client.MV_SKIP_ACTION
            )
        )
        self.assertFalse(
            common_client.is_microversion_supported(
                '1.4', common_client.MV_SKIP_ACTION
            )
        )
        self.assertFalse(
            common_client.is_microversion_supported(
                '1.1', common_client.MV_SKIP_ACTION
            )
        )
        self.assertFalse(
            common_client.is_microversion_supported(
                None, common_client.MV_SKIP_ACTION
            )
        )
