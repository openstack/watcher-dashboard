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

from horizon.test.settings import *  # noqa
from openstack_dashboard.test.settings import *  # noqa

# Load the pluggable dashboard settings
import openstack_dashboard.enabled
import watcher_dashboard.local.enabled

INSTALLED_APPS = (
    'django.contrib.contenttypes',
    'django.contrib.auth',
    'django.contrib.sessions',
    'django.contrib.staticfiles',
    'django.contrib.messages',
    'django.contrib.humanize',
    'openstack_auth',
    'compressor',
    'horizon',
    'openstack_dashboard',
)

INSTALLED_APPS = list(INSTALLED_APPS)  # Make sure it's mutable
settings_utils.update_dashboards(
    [
        watcher_dashboard.local.enabled,
        openstack_dashboard.enabled,
    ],
    HORIZON_CONFIG,
    INSTALLED_APPS,
)
