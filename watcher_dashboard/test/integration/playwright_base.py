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

"""Base test class for Playwright integration tests."""

import os
import re
import time

import fixtures

from keystoneauth1 import identity
from keystoneauth1 import session as keystone_session
from oslo_log import log
from oslotest import base
from playwright import sync_api
from watcherclient import client as watcher_client
from watcherclient.common.apiclient import exceptions as watcher_exceptions

from watcher_dashboard.test.integration import playwright_config as config


LOG = log.getLogger(__name__)


class PlaywrightFixture(fixtures.Fixture):
    """Fixture to manage Playwright browser lifecycle.

    This handles starting Playwright, launching the browser, creating the
    context (with video/tracing configuration), and creating the page.
    """

    def __init__(self, use_auth_reuse=False):
        super().__init__()
        self.use_auth_reuse = use_auth_reuse
        self.playwright = None
        self.browser = None
        self.context = None
        self.page = None

    def _setUp(self):
        # 1. Start Playwright
        self.playwright = sync_api.sync_playwright().start()
        self.addCleanup(self.playwright.stop)

        # 2. Launch Browser
        browser_type = config.get_browser()
        launchers = {
            'chromium': self.playwright.chromium,
            'firefox': self.playwright.firefox,
            'webkit': self.playwright.webkit,
        }
        launcher = launchers[browser_type]

        self.browser = launcher.launch(headless=config.is_headless())
        self.addCleanup(self.browser.close)

        # 3. Configure Context (Video, Viewport, Auth)
        video_dir = self._get_video_dir()
        context_kwargs = {
            'viewport': {'width': 1920, 'height': 1080},
            'ignore_https_errors': config.ignore_https_errors(),
        }
        if video_dir:
            context_kwargs.update(
                {
                    'record_video_dir': video_dir,
                    'record_video_size': {'width': 1920, 'height': 1080},
                }
            )

        # Handle Auth State Reuse
        auth_path = config.get_auth_state_path()
        if self.use_auth_reuse and os.path.exists(auth_path):
            context_kwargs['storage_state'] = auth_path
            LOG.info("Reusing auth state from: %s", auth_path)

        self.context = self.browser.new_context(**context_kwargs)
        self.context.set_default_timeout(config.get_timeout())
        self.addCleanup(self._close_context_and_finalize_artifacts)

        # 4. Start Tracing if enabled
        if config.get_trace_mode() != 'off':
            self.context.tracing.start(
                screenshots=True, snapshots=True, sources=True
            )

        # 5. Create Page
        self.page = self.context.new_page()

    def _get_video_dir(self):
        """Return the video recording directory, or None if disabled."""
        if config.get_video_mode() == 'off':
            return None
        video_dir = config.get_video_dir()
        os.makedirs(video_dir, exist_ok=True)
        return video_dir

    def _close_context_and_finalize_artifacts(self):
        """Close context and handle video/trace retention logic."""
        # Capture paths before closing
        video_path = None
        if self.page.video:
            try:
                video_path = self.page.video.path()
            except (OSError, AttributeError) as e:
                LOG.debug("Failed to get video path: %s", e)

        trace_path = None
        trace_mode = config.get_trace_mode()
        if trace_mode != 'off':
            trace_dir = config.get_trace_dir()
            os.makedirs(trace_dir, exist_ok=True)
            # We use a generic name here, simpler than passing test names
            # into fixture
            trace_path = os.path.join(trace_dir, f"trace_{id(self)}.zip")
            try:
                self.context.tracing.stop(path=trace_path)
            except (OSError, AttributeError) as e:
                LOG.warning("Failed to save trace: %s", e)

        self.context.close()

        # Handle "retain-on-failure" logic
        # Note: In fixtures, we don't easily know pass/fail status of the
        # test unless passed in. For simplicity, we default to keeping
        # artifacts or you can hook into testtools.TestCase.addOnException
        # to delete them only on success.
        # A common simple pattern: Keep them, let CI clean up.
        if video_path:
            LOG.info("Video saved to: %s", video_path)


class WatcherClientFixture(fixtures.Fixture):
    """Session-scoped fixture for Watcher API client.

    Provides a python-watcherclient instance authenticated via keystoneauth1.
    Used for fast, reliable resource cleanup via Watcher API.
    """

    def __init__(self):
        super().__init__()
        self.client = None

    def _setUp(self):
        auth = identity.Password(
            auth_url=config.get_auth_url(),
            username=config.get_username(),
            password=config.get_password(),
            project_name=config.get_project_name(),
            user_domain_name=config.get_user_domain_name(),
            project_domain_name=config.get_project_domain_name(),
        )
        session = keystone_session.Session(
            auth=auth, verify=not config.is_insecure()
        )
        self.client = watcher_client.Client('1', session=session)
        LOG.info("Watcher API client initialized for test cleanup")


class PlaywrightTestCase(base.BaseTestCase):
    """Base test case for Watcher Dashboard Integration tests.

    Uses oslotest and fixtures for standard resource management.
    """

    # Convenience alias for Playwright expect assertions
    expect = sync_api.expect

    # Subclasses can set this to False to skip the automatic login in setUp().
    auto_login = True

    @property
    def watcher_client(self):
        """Get the Watcher API client for cleanup operations.

        :returns: Watcher API client instance
        """
        return self._watcher_client_fixture.client

    def setUp(self):
        """Set up test fixtures."""
        super().setUp()

        self.dashboard_url = config.get_dashboard_url()
        self.screenshot_dir = config.get_screenshot_dir()

        # Initialize Watcher API client at test level
        self._watcher_client_fixture = self.useFixture(WatcherClientFixture())

        # Initialize Playwright via Fixture
        self.pw_fixture = self.useFixture(
            PlaywrightFixture(use_auth_reuse=config.is_auth_reuse_enabled())
        )
        self.page = self.pw_fixture.page

        # Ensure screenshot dir exists
        if config.is_screenshot_enabled():
            os.makedirs(self.screenshot_dir, exist_ok=True)

        self._screenshot_counter = 0
        self._test_screenshot_dir = self._get_test_screenshot_dir()
        if self._test_screenshot_dir:
            os.makedirs(self._test_screenshot_dir, exist_ok=True)

        if self.auto_login:
            self.login()

    def login(self):
        """Log in to the Dashboard. Uses auth reuse if configured."""
        self.page.goto(self.dashboard_url)
        self.take_screenshot("dashboard_loaded")

        if '/auth/login' not in self.page.url:
            LOG.info("Already authenticated, skipping login form.")
            self.take_screenshot("dashboard_authenticated")
            return

        self.take_screenshot("login_page")
        self.page.get_by_label("User Name").fill(config.get_username())
        self.take_screenshot("login_username_filled")
        self.page.get_by_label("Password").fill(config.get_password())
        self.take_screenshot("login_password_filled")
        # Custom dashboard could have different login button name
        # Using locator will help to avoid checking for specific button
        # label.
        self.page.locator("#loginBtn").click()
        self.take_screenshot("login_submit")

        # Wait for login to complete
        sync_api.expect(self.page).not_to_have_url(
            re.compile(r".*/auth/login.*"), timeout=config.get_timeout()
        )
        self.take_screenshot("dashboard_logged_in")

        # Save auth state if enabled
        if config.is_auth_reuse_enabled():
            auth_path = config.get_auth_state_path()
            os.makedirs(os.path.dirname(auth_path), exist_ok=True)
            self.pw_fixture.context.storage_state(path=auth_path)

    def take_screenshot(self, name):
        """Helper to take numbered screenshots."""
        if not config.is_screenshot_enabled():
            return

        self._screenshot_counter += 1
        filename = f"{self._screenshot_counter:03d}_{name}.png"
        if self._test_screenshot_dir:
            base_dir = self._test_screenshot_dir
        else:
            base_dir = self.screenshot_dir
        path = os.path.join(base_dir, filename)
        self.page.screenshot(path=path)
        return path

    def _get_test_screenshot_dir(self):
        """Return a per-test screenshot directory.

        This avoids filename collisions when tests run in parallel and when
        multiple tests generate the same screenshot names.
        """
        if not config.is_screenshot_enabled():
            return None
        test_id = self.id()
        safe_test_id = re.sub(r'[^A-Za-z0-9_.-]+', '_', test_id)
        return os.path.join(self.screenshot_dir, safe_test_id)

    def create_audit_template(
        self, name, goal_name="Dummy goal", strategy_name="Dummy strategy"
    ):
        """Create an audit template and register cleanup.

        :param name: Name of the audit template to create
        :type name: str
        :param goal_name: Goal name to select in the dropdown
        :type goal_name: str
        :param strategy_name: Strategy name to select in the dropdown
        :type strategy_name: str
        """
        self.page.goto(f"{self.dashboard_url}/admin/audit_templates/")
        self.take_screenshot("audit_templates_page_loaded")

        self.page.get_by_role("link", name="Create Template").click()
        self.take_screenshot("audit_template_modal_open")
        modal_header = self.page.get_by_role(
            "heading", name="Create Audit Template"
        )
        sync_api.expect(modal_header).to_be_visible()

        self.page.get_by_label("Name").fill(name)
        self.take_screenshot("audit_template_name_filled")
        self.page.get_by_label("Goal").select_option(label=goal_name)
        self.take_screenshot("audit_template_goal_selected")
        self.page.get_by_label("Strategy").select_option(label=strategy_name)
        self.take_screenshot("audit_template_strategy_selected")

        self.page.get_by_role("button", name="Create Audit Template").click()
        self.take_screenshot("audit_template_submit")
        self.wait_for_success_message()
        self.take_screenshot("audit_template_created")

        template_uuid = self.watcher_client.audit_template.get(name).uuid

        self.addCleanup(self._delete_audit_template_via_api, template_uuid)

        return template_uuid

    def create_audit(self, template_name, audit_name, audit_type="ONESHOT"):
        """Create an audit and register cleanup.

        :param template_name: Name of the audit template to use
        :type template_name: str
        :param audit_name: Name for the audit
        :type audit_name: str
        :param audit_type: Type of audit
        :type audit_type: str
        :returns: The audit name
        """
        self.page.goto(f"{self.dashboard_url}/admin/audits/")
        self.take_screenshot("audits_page_loaded")

        # The button to open modal - prefer user-visible text over classes.
        try:
            create_link = self.page.get_by_role("link", name="Create Audit")
            create_link.click()
        except sync_api.TimeoutError:
            create_link = self.page.get_by_role("link", name="New Audit")
            create_link.click()
        self.take_screenshot("audit_modal_open")

        modal_header = self.page.get_by_role("heading", name="Create Audit")
        sync_api.expect(modal_header).to_be_visible()

        # Select template
        self.page.get_by_label("Template").select_option(label=template_name)
        self.take_screenshot("audit_template_selected")

        # Fill audit name
        self.page.get_by_label("Name").fill(audit_name)
        self.take_screenshot("audit_name_filled")

        # Select audit type - must always be explicitly selected as no default
        self.page.get_by_label("Type").select_option(label=audit_type)
        self.take_screenshot("audit_type_selected")

        # Submit the form
        self.page.get_by_role("button", name="Create Audit").click()
        self.take_screenshot("audit_submit")

        self.wait_for_success_message()
        self.take_screenshot("audit_created")

        audit_uuid = self._get_audit_uuid_via_api(audit_name)

        self.addCleanup(self._delete_audit_via_api, audit_uuid)
        self.addCleanup(
            self._delete_action_plans_for_audit_via_api, audit_uuid
        )

        return audit_uuid

    def _delete_audit_template_via_api(self, template_uuid):
        """Delete an audit template using the Watcher API.

        :param template_uuid: UUID of the audit template to delete
        :type template_uuid: str
        """
        LOG.info("API cleanup: deleting audit template uuid=%s", template_uuid)
        try:
            self.watcher_client.audit_template.delete(template_uuid)
            LOG.info(
                "API cleanup: deleted audit template uuid=%s", template_uuid
            )
        except watcher_exceptions.ClientException as exc:
            LOG.error(
                "API cleanup FAILED for audit template uuid=%s: %s",
                template_uuid,
                exc,
            )

    def _delete_audit_via_api(self, audit_uuid):
        """Delete an audit using the Watcher API.

        :param audit_uuid: UUID of the audit to delete
        :type audit_uuid: str
        """
        LOG.info("API cleanup: deleting audit uuid=%s", audit_uuid)
        try:
            self.watcher_client.audit.delete(audit_uuid)
            LOG.info("API cleanup: deleted audit uuid=%s", audit_uuid)
        except watcher_exceptions.ClientException as exc:
            LOG.error(
                "API cleanup FAILED for audit uuid=%s: %s", audit_uuid, exc
            )

    def _delete_action_plans_for_audit_via_api(self, audit_uuid):
        """Delete action plans associated with a specific audit.

        :param audit_uuid: UUID of the audit whose action plans to delete
        :type audit_uuid: str
        """
        LOG.info(
            "API cleanup: deleting action plans for audit uuid=%s...",
            audit_uuid,
        )
        try:
            action_plans = self.watcher_client.action_plan.list(
                audit=audit_uuid
            )
            for action_plan in action_plans:
                self.watcher_client.action_plan.delete(action_plan.uuid)
                LOG.info(
                    "API cleanup: deleted action plan (uuid=%s)",
                    action_plan.uuid,
                )
        except watcher_exceptions.ClientException as exc:
            LOG.error("API cleanup FAILED for action plans: %s", exc)

    def _get_audit_uuid_via_api(self, audit_name):
        """Look up an audit UUID by name via the Watcher API.

        :param audit_name: Name of the audit
        :type audit_name: str
        :returns: The audit UUID, or None if not found
        :rtype: str or None
        """
        try:
            audit = self.watcher_client.audit.get(audit_name)
            if audit:
                return audit.uuid
            LOG.warning("Could not resolve UUID for audit '%s'", audit_name)
        except watcher_exceptions.ClientException as exc:
            LOG.error(
                "Failed to resolve UUID for audit '%s': %s", audit_name, exc
            )
        return None

    def wait_for_success_message(self, timeout=None):
        """Wait for success message to appear.

        :param timeout: Timeout in milliseconds (default: config timeout)
        :type timeout: int
        """
        if timeout is None:
            timeout = config.get_timeout()
        # Try multiple selectors for success message
        success_msg = (
            self.page.get_by_role("alert")
            .or_(self.page.get_by_text("Success"))
            .or_(self.page.get_by_text("Successfully"))
            .first
        )
        sync_api.expect(success_msg).to_be_visible(timeout=timeout)

    def wait_for_audit_status(self, status, timeout=120, poll_interval=5):
        """Wait for audit status with polling.

        :param status: Expected status string
        :type status: str
        :param timeout: Maximum time to wait in seconds
        :type timeout: int
        :param poll_interval: Time between polls in seconds
        :type poll_interval: int
        :raises TimeoutError: If status is not reached within timeout
        """
        start_time = time.time()

        while time.time() - start_time < timeout:
            self.page.reload()
            if self.page.get_by_text(status, exact=True).count() > 0:
                return
            time.sleep(poll_interval)

        raise TimeoutError("Audit did not reach %s in %ss" % (status, timeout))
