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

"""Integration tests for audit template scope format validation."""

import json
import textwrap
import uuid

from django import test

from watcher_dashboard.test.integration import playwright_base


@test.tag('integration')
class AuditTemplateScopeFormatTests(playwright_base.PlaywrightTestCase):
    """Tests for YAML and JSON scope input on audit template creation."""

    def _generate_unique_name(self, prefix):
        """Generate a unique resource name for test isolation."""
        return f"{prefix}_{uuid.uuid4().hex[:8]}"

    def _verify_scope_in_detail_view(self, row, template_name, label):
        """Click through to detail view and verify scope is displayed."""
        row.get_by_role("link", name=template_name).click()
        self.take_screenshot(f"audit_template_{label}_detail_view")
        self.expect(self.page.get_by_text("Audit Scope")).to_be_visible()
        scope_section = self.page.locator("code")
        self.expect(scope_section).to_be_visible()
        self.expect(scope_section).to_contain_text("host-agg-01")
        self.expect(scope_section).to_contain_text("compute-node-01")
        self.take_screenshot(f"audit_template_{label}_detail_verified")

    def test_create_audit_template_with_yaml_scope(self):
        """Test creating an audit template with a valid YAML scope.

        Steps:
            1. Navigate to the Audit Templates index page
            2. Create a new audit template with a YAML scope value
            3. Verify the template appears in the table
            4. Click the template to navigate to the detail view
            5. Verify the scope is displayed in the detail view

        Expected Result:
            The audit template should be created successfully with the
            YAML scope, be visible in the index table, and show the
            scope in the detail view.
        """
        template_name = self._generate_unique_name("test_yaml_scope")
        yaml_scope = textwrap.dedent("""\
            - compute:
              - host_aggregates:
                - name: host-agg-01
              - exclude:
                - compute_nodes:
                  - name: compute-node-01
                  - name: compute-node-02
                  - name: compute-node-03
        """)

        self.create_audit_template(
            template_name,
            goal_name="Workload Balancing",
            strategy_name="Workload Balance Migration Strategy",
            scope=yaml_scope,
        )

        row = self.page.get_by_role("row").filter(has_text=template_name)
        self.expect(row).to_be_visible()
        self.take_screenshot("audit_template_yaml_scope_created")

        self._verify_scope_in_detail_view(row, template_name, "yaml_scope")

    def test_create_audit_template_with_json_scope(self):
        """Test creating an audit template with a valid JSON scope.

        Steps:
            1. Navigate to the Audit Templates index page
            2. Create a new audit template with a JSON scope value
            3. Verify the template appears in the table
            4. Click the template to navigate to the detail view
            5. Verify the scope is displayed in the detail view

        Expected Result:
            The audit template should be created successfully with the
            JSON scope, be visible in the index table, and show the
            scope in the detail view.
        """
        template_name = self._generate_unique_name("test_json_scope")
        json_scope = json.dumps(
            [
                {
                    "compute": [
                        {"host_aggregates": [{"name": "host-agg-01"}]},
                        {
                            "exclude": [
                                {
                                    "compute_nodes": [
                                        {"name": "compute-node-01"},
                                        {"name": "compute-node-02"},
                                        {"name": "compute-node-03"},
                                    ]
                                }
                            ]
                        },
                    ]
                }
            ]
        )

        self.create_audit_template(
            template_name,
            goal_name="Workload Balancing",
            strategy_name="Workload Balance Migration Strategy",
            scope=json_scope,
        )

        row = self.page.get_by_role("row").filter(has_text=template_name)
        self.expect(row).to_be_visible()
        self.take_screenshot("audit_template_json_scope_created")

        self._verify_scope_in_detail_view(row, template_name, "json_scope")

    def test_audit_template_scope_invalid_input(self):
        """Test that invalid YAML/JSON scope is rejected by form validation.

        Steps:
            1. Navigate to the Audit Templates index page
            2. Open the create audit template modal
            3. Fill required fields and enter invalid scope content
            4. Submit the form and verify it is rejected

        Expected Result:
            The modal should remain visible with the validation error
            message for each invalid input.
        """
        invalid_inputs = {
            "invalid_yaml": "{invalid: yaml: [",
            "invalid_json": '[{"compute": [}]',
        }

        for label, scope_value in invalid_inputs.items():
            with self.subTest(input_type=label):
                self.page.goto(f"{self.dashboard_url}/admin/audit_templates/")
                self.page.get_by_role("link", name="Create Template").click()

                modal_header = self.page.get_by_role(
                    "heading", name="Create Audit Template"
                )
                self.expect(modal_header).to_be_visible()

                template_name = self._generate_unique_name(label)
                self.page.get_by_label("Name").fill(template_name)
                self.page.get_by_label("Goal").select_option(
                    label="Workload Balancing"
                )
                self.page.get_by_label("Strategy").select_option(
                    label="Workload Balance Migration Strategy"
                )
                self.page.locator("#id_scope").fill(scope_value)
                self.take_screenshot(f"scope_{label}_filled")

                self.page.get_by_role(
                    "button", name="Create Audit Template"
                ).click()
                self.take_screenshot(f"scope_{label}_submitted")

                self.expect(modal_header).to_be_visible()
                error_msg = self.page.get_by_text(
                    "Enter a valid YAML or JSON value."
                )
                self.expect(error_msg).to_be_visible()
                self.take_screenshot(f"scope_{label}_validation_error")
