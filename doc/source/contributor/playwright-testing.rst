===============================
Playwright Integration Tests
===============================

This guide covers how to set up and run Playwright-based integration tests
for the Watcher Dashboard.

Prerequisites
=============

Before running Playwright tests, create the tox virtualenv and install the
browser binary along with its system dependencies. This is a one-time setup
per system.

.. code-block:: bash

   cd watcher-dashboard

   # 1. Create the tox venv (installs pinned Playwright version)
   tox -e venv -- python3 -m playwright --version

   # 2. Install OS-level libraries required by the browser
   sudo .tox/venv/bin/playwright install-deps webkit

   # 3. Install the browser binary
   .tox/venv/bin/python3 -m playwright install webkit

   # For other browsers, replace 'webkit' with 'chromium' or 'firefox'

.. note::

   In CI, these same steps are performed automatically by
   ``playbooks/playwright/pre.yaml``. Tox itself does not install browser
   binaries.

Running Tests
=============

Basic Usage
-----------

.. code-block:: bash

   # Source OpenStack credentials first
   source ~/repos/devstack/openrc admin admin

   # Default: WebKit, headless — run all integration tests
   tox -e integration-playwright -- integration

   # Run a specific test module (stestr regex)
   tox -e integration-playwright -- test_playwright_audit_workflow

   # Run a single test method (full dotted path)
   tox -e integration-playwright -- watcher_dashboard.test.integration.test_playwright_audit_workflow.AuditWorkflowTests.test_launch_audit_and_verify_action_plan

   # Run tests matching a pattern
   tox -e integration-playwright -- "test_audit"

Recording Modes
---------------

Playwright captures screenshots, videos, and traces for debugging.

.. list-table:: Recording Configuration
   :header-rows: 1
   :widths: 15 25 15 45

   * - Artifact
     - Environment Variable
     - Default
     - Description
   * - Screenshots
     - ``PLAYWRIGHT_SCREENSHOTS``
     - ``True``
     - Explicit screenshots taken at key test actions. Set to ``False``
       to disable.
   * - Video
     - ``PLAYWRIGHT_VIDEO``
     - ``off``
     - Record video of browser during test execution.
   * - Trace
     - ``PLAYWRIGHT_TRACE``
     - ``off``
     - Detailed trace (DOM snapshots, network, console logs).


.. list-table:: Video and Trace Modes
   :header-rows: 1
   :widths: 20 80

   * - Mode
     - Behavior
   * - ``off``
     - No recording (default).
   * - ``on``
     - Always record and keep artifacts.
   * - ``retain-on-failure``
     - Record but delete if test passes. **Recommended for CI**.

.. note::

   CI runs use ``retain-on-failure`` for both video and trace — this is
   already configured in ``.zuul.yaml`` and requires no manual setup.

Viewing Traces
^^^^^^^^^^^^^^

Upload trace zip files to https://trace.playwright.dev (drag and drop), or:

.. code-block:: bash

   .tox/integration-playwright/bin/playwright show-trace \
       playwright/traces/trace_<id>.zip

Environment Variables
---------------------

.. list-table::
   :header-rows: 1
   :widths: 35 65

   * - Variable
     - Description
   * - ``PLAYWRIGHT_BROWSER``
     - Browser: ``chromium``, ``firefox``, or ``webkit`` (default)
   * - ``PLAYWRIGHT_HEADLESS``
     - Headless mode: ``True`` (default) or ``False``
   * - ``PLAYWRIGHT_TIMEOUT``
     - Default timeout in ms (default: ``30000``)
   * - ``PLAYWRIGHT_OUTPUT_DIR``
     - Base directory for all artifacts (default: ``playwright/``)
   * - ``PLAYWRIGHT_AUTH_REUSE``
     - Reuse login state: ``True`` (default) or ``False``
   * - ``WATCHER_DASHBOARD_URL``
     - Dashboard URL (default: ``http://localhost/dashboard``)
   * - ``OS_USERNAME``
     - Login username (default: ``admin``)
   * - ``OS_PASSWORD``
     - Login password (default: ``secretadmin``)
   * - ``OS_INSECURE``
     - Disable SSL verification: ``True`` (default) or ``False``

Artifacts are stored under ``PLAYWRIGHT_OUTPUT_DIR``
(default: ``playwright/``):

.. code-block:: text

   playwright/
   ├── .auth/           # Saved authentication state
   ├── screenshots/     # Explicit, named screenshots from tests
   ├── videos/          # Test execution videos
   └── traces/          # Trace zip files

.. note::

   The ``playwright/`` directory is automatically deleted at the start of
   each tox run to ensure clean test artifacts.

Writing Tests
-------------

.. code-block:: python

   from watcher_dashboard.test.integration import playwright_base
   from playwright import sync_api as playwright_sync


   class MyTests(playwright_base.PlaywrightTestCase):

       def test_create_template(self):
           template_name = "my_template"
           # Create with automatic API cleanup; returns the UUID
           self.create_audit_template(template_name)

           # Verify the template appears in the table
           row = self.page.get_by_role("row").filter(has_text=template_name)
           self.expect(row).to_be_visible()

The base class logs in at the start of each test and registers API cleanup
for created audit templates and audits using ``python-watcherclient``.

Screenshots are taken explicitly in the base helpers and tests using
``self.take_screenshot("name")`` so the output names describe the action.

