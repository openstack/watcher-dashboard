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

"""Test mixin classes for watcher-dashboard unit tests.

Provides mixins that manage test isolation for modules that use memoized
caching, preventing cached state from leaking between test cases.
"""

from watcher_dashboard import config


class ConfigMemoizedCache:
    """Mixin that clears memoized config caches before and after each test.

    Use this mixin in test cases that exercise ``watcher_dashboard.config``
    functions decorated with ``@functools.lru_cache`` or similar caching
    decorators. It ensures each test starts and ends with a clean cache
    state, preventing cross-test pollution.

    Example::

        from watcher_dashboard.test.local_fixtures.fixtures import (
            ConfigMemoizedCache,
        )


        class TestConfigFunctions(ConfigMemoizedCache, TestCase):
            def test_get_ssl_no_verify_default(self):
                result = config.get_ssl_no_verify()
                self.assertFalse(result)
    """

    def setUp(self):
        super().setUp()
        self._clear_config_caches()

    def tearDown(self):
        super().tearDown()
        self._clear_config_caches()

    def _clear_config_caches(self):
        """Clear all ``functools`` caches on ``watcher_dashboard.config``."""
        for attr_name in dir(config):
            attr = getattr(config, attr_name)
            if callable(attr) and hasattr(attr, 'cache_clear'):
                attr.cache_clear()
