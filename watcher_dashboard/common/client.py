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
from watcherclient.common import api_versioning
from watcherclient import exceptions as wc_exc

LOG = logging.getLogger(__name__)

# Service type used by Watcher in the catalog
WATCHER_SERVICE = 'infra-optim'

# Default/minimal microversion
MIN_DEFAULT = '1.0'

# Microversion enabling audit start/end time fields
MV_START_END = '1.1'


def get_client(request, required=MIN_DEFAULT):
    """Return a watcher client pinned to the given microversion.

    :param request: The current Django HTTP request.
    :param required: Microversion string (e.g. ``'1.0'``,
        ``'1.1'``).
    """
    endpoint = base.url_for(request, WATCHER_SERVICE)
    insecure = settings.OPENSTACK_SSL_NO_VERIFY
    ca_file = settings.OPENSTACK_SSL_CACERT

    return wc.get_client(
        '1',
        watcher_url=endpoint,
        insecure=insecure,
        ca_file=ca_file,
        username=request.user.username,
        os_auth_token=request.user.token.id,
        os_infra_optim_api_version=required,
    )


def get_max_version(request):
    """Discover the server's maximum supported microversion.

    Queries the Watcher API root endpoint and extracts the
    ``max_version`` field from the response body.

    :param request: The current Django HTTP request.
    :returns: The max version string, or ``None`` on failure.
    """
    try:
        client = get_client(request)
        _resp, body = client.http_client.json_request(
            'GET', '/')
        version_info = (
            body.get('versions') or
            body.get('version') or
            body.get('default_version') or
            {})
        if isinstance(version_info, list) and version_info:
            version_info = version_info[0]
        if isinstance(version_info, dict):
            return version_info.get('max_version')
    except wc_exc.ClientException:
        LOG.debug('Microversion discovery failed',
                  exc_info=True)
    return None


def is_microversion_supported(max_ver, required):
    """Check whether the server supports the required microversion.

    :param max_ver: The server's max version string from
        :func:`get_max_version`, or ``None``.
    :param required: The microversion string to check
        (e.g. ``'1.1'``).
    :returns: ``True`` if the server's max version is at least
        *required*, ``False`` otherwise.
    """
    if max_ver is None:
        return False
    try:
        return (api_versioning.APIVersion(max_ver) >=
                api_versioning.APIVersion(required))
    except (wc_exc.UnsupportedVersion, TypeError):
        return False
