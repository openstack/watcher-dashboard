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

from django.conf import settings
from django.test import TestCase
from django.test import override_settings

from watcher_dashboard import config
from watcher_dashboard.tests.local_fixtures.fixtures import ConfigMemoizedCache


class ConfigTests(ConfigMemoizedCache, TestCase):
    # --- get_ssl_no_verify ---

    def test_get_ssl_no_verify_default(self):
        # OPENSTACK_SSL_NO_VERIFY is absent from test settings; expect False.
        result = config.get_ssl_no_verify()
        self.assertFalse(result)

    @override_settings(OPENSTACK_SSL_NO_VERIFY=True)
    def test_get_ssl_no_verify_true(self):
        result = config.get_ssl_no_verify()
        self.assertTrue(result)

    @override_settings(OPENSTACK_SSL_NO_VERIFY=1)
    def test_get_ssl_no_verify_coerces_truthy_int(self):
        result = config.get_ssl_no_verify()
        self.assertIs(result, True)

    # --- get_ssl_cacert ---

    def test_get_ssl_cacert_default(self):
        # OPENSTACK_SSL_CACERT is absent from test settings; expect None.
        result = config.get_ssl_cacert()
        self.assertIsNone(result)

    @override_settings(OPENSTACK_SSL_CACERT='')
    def test_get_ssl_cacert_empty_string(self):
        result = config.get_ssl_cacert()
        self.assertIsNone(result)

    @override_settings(OPENSTACK_SSL_CACERT='/etc/ssl/certs/ca.pem')
    def test_get_ssl_cacert_value(self):
        result = config.get_ssl_cacert()
        self.assertEqual(result, '/etc/ssl/certs/ca.pem')

    @override_settings(OPENSTACK_SSL_CACERT=42)
    def test_get_ssl_cacert_invalid_type(self):
        self.assertRaises(TypeError, config.get_ssl_cacert)

    # --- get_policy_files ---

    @override_settings(POLICY_FILES={})
    def test_get_policy_files_default(self):
        # POLICY_FILES is an empty dict; function should return {}.
        result = config.get_policy_files()
        self.assertEqual(result, {})

    @override_settings(POLICY_FILES='not-a-dict')
    def test_get_policy_files_invalid_type(self):
        self.assertRaises(TypeError, config.get_policy_files)

    # --- set_policy_file ---

    @override_settings(POLICY_FILES={})
    def test_set_policy_file(self):
        config.set_policy_file('infra-optim', 'watcher_policy.yaml')
        result = config.get_policy_files()
        self.assertEqual(result.get('infra-optim'), 'watcher_policy.yaml')

    @override_settings(POLICY_FILES={'other': 'other.yaml'})
    def test_set_policy_file_shallow_copy(self):
        before = settings.POLICY_FILES
        config.set_policy_file('infra-optim', 'watcher_policy.yaml')
        self.assertEqual(before, {'other': 'other.yaml'})
        self.assertEqual(
            config.get_policy_files().get('infra-optim'), 'watcher_policy.yaml'
        )

    def test_set_policy_file_empty_service(self):
        self.assertRaises(ValueError, config.set_policy_file, '', 'some.yaml')

    def test_set_policy_file_empty_filename(self):
        self.assertRaises(ValueError, config.set_policy_file, 'svc', '')
