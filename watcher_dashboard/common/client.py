#    Licensed under the Apache License, Version 2.0 (the "License"); you may
#    not use this file except in compliance with the License. You may obtain
#    a copy of the License at
##
#         http://www.apache.org/licenses/LICENSE-2.0
##
#    Unless required by applicable law or agreed to in writing, software
#    distributed under the License is distributed on an "AS IS" BASIS, WITHOUT
#    WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the
#    License for the specific language governing permissions and limitations
#    under the License.

import logging

from django.conf import settings
from openstack_dashboard.api import base
from watcherclient import client as wc

LOG = logging.getLogger(__name__)

# Service type used by Watcher in the catalog
WATCHER_SERVICE = 'infra-optim'

# Common header name used by OpenStack microversioning
HEADER_NAME = 'OpenStack-API-Version'

# Default/minimal microversion
MIN_DEFAULT = '1.0'

# Microversion enabling audit start/end time fields
MV_START_END = '1.1'


def get_client(request, required=MIN_DEFAULT):
    """Return a watcher client pinned to the given microversion.

    'required' can be '1.0', '1.1', or 'latest'.
    """
    endpoint = base.url_for(request, WATCHER_SERVICE)
    insecure = getattr(settings, 'OPENSTACK_SSL_NO_VERIFY', False)
    ca_file = getattr(settings, 'OPENSTACK_SSL_CACERT', None)

    return wc.get_client(
        '1',
        watcher_url=endpoint,
        insecure=insecure,
        ca_file=ca_file,
        username=request.user.username,
        os_auth_token=request.user.token.id,
        os_infra_optim_api_version=required,
    )
