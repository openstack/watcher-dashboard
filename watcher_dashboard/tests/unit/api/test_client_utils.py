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

from watcher_dashboard.common import client as common_client
from watcher_dashboard.tests import helpers as test


class MicroversionSupportTests(test.TestCase):
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
