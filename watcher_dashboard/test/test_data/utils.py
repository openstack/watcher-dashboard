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

from openstack_dashboard.test.test_data import keystone_data
from openstack_dashboard.test.test_data import utils


def load_test_data(load_onto=None):
    from watcher_dashboard.test.test_data import exceptions
    from watcher_dashboard.test.test_data import watcher_data

    # The order of these loaders matters, some depend on others.
    loaders = (exceptions.data,
               keystone_data.data,
               watcher_data.data)
    if load_onto:
        for data_func in loaders:
            data_func(load_onto)
        return load_onto
    else:
        return utils.TestData(*loaders)


class TestDataContainer(utils.TestDataContainer):
    def filter(self, filtered=None, **kwargs):
        """Returns objects in this container """
        """whose attributes match the given keyword arguments.
        """
        if filtered is None:
            filtered = self._objects
        try:
            key, value = kwargs.popitem()
        except KeyError:
            # We're out of filters, return
            return filtered

        def get_match(obj):
            return key in obj and obj.get(key) == value

        return self.filter(filtered=filter(get_match, filtered), **kwargs)

    def delete(self):
        """Delete the first object from this container and return a list"""
        self._objects.remove(self._objects[0])
        return self._objects
