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

"""Centralized configuration for Playwright integration tests."""

import functools
import os

from oslo_utils import strutils


VALID_BROWSERS = ('chromium', 'firefox', 'webkit')
VALID_VIDEO_MODES = ('off', 'on', 'retain-on-failure')
VALID_TRACE_MODES = ('off', 'on', 'retain-on-failure')


# OpenStack Configuration (via environment variables)


@functools.cache
def get_username():
    """Get username for dashboard login from environment.

    :returns: Username from OS_USERNAME environment variable
    """
    return os.environ['OS_USERNAME']


@functools.cache
def get_password():
    """Get password for dashboard login from environment.

    :returns: Password from OS_PASSWORD environment variable
    """
    return os.environ['OS_PASSWORD']


@functools.cache
def get_auth_url():
    """Get Keystone auth URL from environment.

    :returns: Auth URL from OS_AUTH_URL environment variable
    """
    return os.environ['OS_AUTH_URL']


@functools.cache
def get_project_name():
    """Get project name from environment.

    :returns: Project name from OS_PROJECT_NAME environment variable
    """
    return os.environ['OS_PROJECT_NAME']


@functools.cache
def get_user_domain_name():
    """Get user domain name from environment.

    :returns: Domain from OS_USER_DOMAIN_NAME environment variable
    """
    return os.environ['OS_USER_DOMAIN_NAME']


@functools.cache
def get_project_domain_name():
    """Get project domain name from environment.

    :returns: Domain from OS_PROJECT_DOMAIN_NAME environment variable
    """
    return os.environ['OS_PROJECT_DOMAIN_NAME']


# Playwright Output Directory (single base, subdirs auto-created)


@functools.cache
def get_output_dir():
    """Get the base directory for all Playwright artifacts.

    Subdirectories (screenshots, videos, traces, .auth) are created
    automatically by the test framework.

    :returns: Base output directory path
    """
    return os.environ['PLAYWRIGHT_OUTPUT_DIR']


@functools.cache
def get_screenshot_dir():
    """Get the directory for saving screenshots.

    :returns: Screenshot directory path
    """
    return os.path.join(get_output_dir(), 'screenshots')


@functools.cache
def get_video_dir():
    """Get the directory for saving video recordings.

    :returns: Video directory path
    """
    return os.path.join(get_output_dir(), 'videos')


@functools.cache
def get_trace_dir():
    """Get the directory for saving trace files.

    :returns: Trace directory path
    """
    return os.path.join(get_output_dir(), 'traces')


@functools.cache
def get_auth_state_path():
    """Get the path for storing authentication state.

    :returns: Auth state file path
    """
    return os.path.join(get_output_dir(), '.auth', 'state.json')


@functools.cache
def get_dashboard_url():
    """Get the Watcher Dashboard URL from environment variable.

    :returns: Dashboard URL
    """
    return os.environ['WATCHER_DASHBOARD_URL']


@functools.cache
def get_browser():
    """Get the browser type for Playwright.

    Supported browsers: chromium, firefox, webkit

    :returns: Browser type
    :raises ValueError: If browser type is not supported
    """
    browser = os.environ['PLAYWRIGHT_BROWSER'].lower()
    if browser not in VALID_BROWSERS:
        raise ValueError(
            "Invalid browser '%s'. Must be one of: %s"
            % (browser, VALID_BROWSERS)
        )
    return browser


@functools.cache
def is_headless():
    """Check if browser should run in headless mode.

    :returns: True if headless mode is enabled
    """
    return strutils.bool_from_string(
        os.environ['PLAYWRIGHT_HEADLESS'], strict=True
    )


@functools.cache
def get_timeout():
    """Get the default timeout for Playwright operations in milliseconds.

    :returns: Timeout in milliseconds
    """
    return int(os.environ['PLAYWRIGHT_TIMEOUT'])


@functools.cache
def is_screenshot_enabled():
    """Check if screenshot generation is enabled.

    :returns: True if screenshots should be taken
    """
    return strutils.bool_from_string(
        os.environ['PLAYWRIGHT_SCREENSHOTS'], strict=True
    )


@functools.cache
def get_video_mode():
    """Get the video recording mode.

    :returns: Video mode: 'off', 'on', or 'retain-on-failure'
    :raises ValueError: If video mode is not supported
    """
    mode = os.environ['PLAYWRIGHT_VIDEO'].lower()
    if mode not in VALID_VIDEO_MODES:
        raise ValueError(
            "Invalid video mode '%s'. Must be one of: %s"
            % (mode, VALID_VIDEO_MODES)
        )
    return mode


@functools.cache
def get_trace_mode():
    """Get the trace recording mode.

    :returns: Trace mode: 'off', 'on', or 'retain-on-failure'
    :raises ValueError: If trace mode is not supported
    """
    mode = os.environ['PLAYWRIGHT_TRACE'].lower()
    if mode not in VALID_TRACE_MODES:
        raise ValueError(
            "Invalid trace mode '%s'. Must be one of: %s"
            % (mode, VALID_TRACE_MODES)
        )
    return mode


@functools.cache
def is_auth_reuse_enabled():
    """Check if authentication state reuse is enabled.

    When enabled, the first login will save browser state and subsequent
    tests will reuse it, avoiding repeated logins.

    :returns: True if auth state reuse is enabled
    """
    return strutils.bool_from_string(
        os.environ['PLAYWRIGHT_AUTH_REUSE'], strict=True
    )


@functools.cache
def is_insecure():
    """Check if SSL certificate verification should be disabled.

    :returns: True if SSL verification should be disabled
    """
    return strutils.bool_from_string(os.environ['OS_INSECURE'], strict=True)
