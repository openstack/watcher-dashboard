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

"""Integration tests for audit workflow using Playwright."""

import uuid

from django import test

from watcher_dashboard.test.integration import playwright_base


@test.tag('integration')
class AuditWorkflowTests(playwright_base.PlaywrightTestCase):
    """Integration tests for audit workflow using Playwright."""

    def _generate_unique_name(self, prefix):
        """Generate a unique resource name for test isolation."""
        return f"{prefix}_{uuid.uuid4().hex[:8]}"

    def test_create_audit_template(self):
        """Test creating an audit template via UI.

        Steps:
            1. Navigate to the Audit Templates index page
            2. Create a new audit template with a unique name
            3. Verify the template appears in the table

        Expected Result:
            The audit template should be created successfully and
            visible in the index table.
        """
        template_name = self._generate_unique_name("test_template")

        self.create_audit_template(template_name)

        # Verify template appears in table
        row = self.page.get_by_role("row").filter(has_text=template_name)
        self.expect(row).to_be_visible()
        self.take_screenshot("audit_template_row_visible")

    def test_launch_audit_and_verify_action_plan(self):
        """Test launching audit and verifying action plan creation.

        Steps:
            1. Create a prerequisite audit template
            2. Create an audit using the template
            3. Wait for the audit to reach SUCCEEDED status
            4. Navigate to action plans page and verify an action plan exists

        Expected Result:
            The audit should complete successfully and generate an
            action plan visible in the action plans table.
        """
        template_name = self._generate_unique_name("test_template")
        self.create_audit_template(template_name)

        audit_name = self._generate_unique_name("test_audit")
        self.create_audit(template_name, audit_name)

        # Wait for audit to complete
        self.wait_for_audit_status("Succeeded")

        # Verify action plan exists
        self.page.goto(f"{self.dashboard_url}/admin/action_plans/")
        self.take_screenshot("action_plans_page_loaded")
        first_row = (
            self.page.get_by_role("row")
            .filter(has=self.page.get_by_role("cell"))
            .first
        )
        self.expect(first_row).to_be_visible()
        self.take_screenshot("action_plans_visible")

    def test_audit_template_form_validation(self):
        """Test that audit template form shows required field validation.

        Steps:
            1. Navigate to the Audit Templates index page
            2. Open the create audit template modal
            3. Attempt to submit the form without filling required fields

        Expected Result:
            The modal should remain visible indicating the form was not
            submitted due to validation errors.
        """
        self.page.goto(f"{self.dashboard_url}/admin/audit_templates/")

        # Open create modal
        self.page.get_by_role("link", name="Create Template").click()

        # Try to submit without filling required fields
        self.page.get_by_role("button", name="Create Audit Template").click()

        # Modal should still be visible (form not submitted)
        modal_header = self.page.get_by_role(
            "heading", name="Create Audit Template"
        )
        self.expect(modal_header).to_be_visible()
        self.take_screenshot("validation_error")
