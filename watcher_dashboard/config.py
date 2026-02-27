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

"""Centralised Django settings access for watcher-dashboard.

All reads of Django settings that were previously scattered via
``getattr``/``setattr`` reflection helpers are consolidated here.
Functions that return immutable values are cached with
``functools.cache`` so repeated look-ups are free; ``set_policy_file``
replaces ``POLICY_FILES`` with a new dict and clears that cache after each
write.
"""

import functools

from django.conf import settings
from oslo_utils import strutils


@functools.cache
def get_ssl_no_verify() -> bool:
    """Return whether SSL verification should be skipped.

    Reads the OPENSTACK_SSL_NO_VERIFY setting.

    Uses oslo_utils.strutils.bool_from_string() so string values like 'False'
    or '0' are handled correctly.  Defaults to False when the setting is
    absent.
    """
    return strutils.bool_from_string(
        getattr(settings, 'OPENSTACK_SSL_NO_VERIFY', False), default=False
    )


@functools.cache
def get_ssl_cacert() -> str | None:
    """Return the CA certificate path (OPENSTACK_SSL_CACERT), or None.

    Returns None when the setting is absent or empty string.
    Raises TypeError if a non-string, non-None value is configured.
    """
    value = getattr(settings, 'OPENSTACK_SSL_CACERT', None)
    if value is None:
        return None
    if not isinstance(value, str):
        raise TypeError(
            f"OPENSTACK_SSL_CACERT must be a str or None, got {type(value)!r}"
        )
    return value or None  # treat empty string as absent


@functools.cache
def get_policy_files() -> dict:
    """Return the POLICY_FILES dict, defaulting to {}.

    Raises TypeError if the setting is present but not a dict.
    """
    value = getattr(settings, 'POLICY_FILES', {})
    if not isinstance(value, dict):
        raise TypeError(f"POLICY_FILES must be a dict, got {type(value)!r}")
    return dict(value)


def set_policy_file(service: str, filename: str) -> None:
    """Register ``filename`` as the policy file for ``service``.

    Both arguments must be non-empty strings.  Replaces ``POLICY_FILES`` with
    a shallow copy plus the new mapping so callers' dicts are not mutated in
    place.  Clears the get_policy_files cache so subsequent reads reflect
    the updated value.
    """
    if not service:
        raise ValueError("service must be a non-empty string")
    if not filename:
        raise ValueError("filename must be a non-empty string")
    raw = getattr(settings, 'POLICY_FILES', {})
    if not isinstance(raw, dict):
        raise TypeError(f"POLICY_FILES must be a dict, got {type(raw)!r}")
    policy_files = dict(raw)
    policy_files[service] = filename
    settings.POLICY_FILES = policy_files
    get_policy_files.cache_clear()
